#!/usr/bin/env python3
"""
Playwright reconnaissance script for CAR/SICAR portals.
Captures HTTP requests, detects SPA stack, captcha, auth, form fields.
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: playwright not installed. Run: pip install playwright")
    sys.exit(1)

try:
    from playwright_stealth import stealth_async
    STEALTH_AVAILABLE = True
except ImportError:
    print("WARNING: playwright_stealth not available, skipping stealth")
    STEALTH_AVAILABLE = False


async def recon_portal(url: str, label: str) -> dict:
    """Reconnaissance for a single portal URL."""
    print(f"\n{'='*70}")
    print(f"RECON: {label}")
    print(f"URL: {url}")
    print(f"{'='*70}\n")

    result = {
        "url": url,
        "label": label,
        "http_status": None,
        "title": "",
        "page_url": "",
        "html_size": 0,
        "stack_markers": [],
        "captcha_detected": [],
        "auth_required": False,
        "form_fields": [],
        "network_requests": [],
        "error": None,
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )

        if STEALTH_AVAILABLE:
            await stealth_async(context)

        page = await context.new_page()

        # Capture all network requests
        captured_requests = []
        captured_responses = []

        def on_request(request):
            captured_requests.append({
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type,
            })

        def on_response(response):
            captured_responses.append({
                "url": response.url,
                "status": response.status,
                "content_type": response.headers.get("content-type", ""),
            })

        page.on("request", on_request)
        page.on("response", on_response)

        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            result["http_status"] = response.status if response else None
        except Exception as e:
            result["error"] = str(e)
            await browser.close()
            return result

        # Capture page metadata
        try:
            result["title"] = await page.title()
        except:
            result["title"] = "(no title)"

        result["page_url"] = page.url

        # Get HTML size
        try:
            html_content = await page.content()
            result["html_size"] = len(html_content)
        except:
            pass

        # Detect SPA markers
        try:
            spa_markers = await page.locator("body").evaluate("""
                el => {
                    const markers = [];

                    // React detection
                    if (document.getElementById('root') || document.getElementById('app')) {
                        markers.push('react:root_or_app_div');
                    }
                    if (window.__NEXT_DATA__ || window.__NEXT_PAGE_PROPS__) {
                        markers.push('nextjs');
                    }
                    if (document.querySelector('[data-reactroot]')) {
                        markers.push('react:data-reactroot');
                    }
                    if (document.querySelector('[data-react-root]')) {
                        markers.push('react:data-react-root');
                    }

                    // Vue detection
                    if (window.__VUE__ || document.querySelector('[v-app]')) {
                        markers.push('vue');
                    }
                    if (document.querySelector('[data-v-app]')) {
                        markers.push('vue:data-v-app');
                    }

                    // Angular detection
                    const htmlTag = document.documentElement;
                    if (htmlTag.getAttribute('ng-version') || htmlTag.getAttribute('ng-app')) {
                        markers.push('angular:ng-version');
                    }

                    return markers;
                }
            """)
            result["stack_markers"].extend(spa_markers)
        except Exception as e:
            pass

        # Detect captcha
        try:
            captcha_check = await page.evaluate("""
                () => {
                    const detected = [];

                    // Check for hCaptcha
                    if (document.querySelector('[data-sitekey]')) {
                        detected.push('hcaptcha_or_recaptcha:sitekey_attribute');
                    }
                    if (document.querySelector('iframe[src*="hcaptcha"]')) {
                        detected.push('hcaptcha:iframe');
                    }
                    if (document.querySelector('iframe[src*="recaptcha"]')) {
                        detected.push('recaptcha:iframe');
                    }

                    // Check script tags
                    const scripts = Array.from(document.querySelectorAll('script'));
                    scripts.forEach(s => {
                        const src = s.src || '';
                        if (src.includes('hcaptcha')) detected.push('hcaptcha:script');
                        if (src.includes('recaptcha')) detected.push('recaptcha:script');
                    });

                    return detected;
                }
            """)
            result["captcha_detected"].extend(captcha_check)
        except Exception as e:
            pass

        # Check for login/auth forms
        try:
            form_check = await page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form, [role="form"]');
                    const fields = [];

                    forms.forEach(form => {
                        const formFields = [];
                        const inputs = form.querySelectorAll('input, select, textarea');
                        inputs.forEach(input => {
                            formFields.push({
                                type: input.type || input.tagName,
                                name: input.name || input.id || '(unnamed)',
                                placeholder: input.placeholder || '',
                                label: Array.from(document.querySelectorAll('label')).find(l => l.htmlFor === input.id)?.textContent || '',
                            });
                        });

                        if (formFields.length > 0) {
                            fields.push({
                                id: form.id || '(unnamed_form)',
                                fields: formFields,
                            });
                        }
                    });

                    // Check for login indicators
                    const pageText = document.body.innerText.toLowerCase();
                    const authRequired = pageText.includes('login') || pageText.includes('autenticação') || pageText.includes('acesso');

                    return { forms: fields, authRequired };
                }
            """)
            result["form_fields"] = form_check.get("forms", [])
            result["auth_required"] = form_check.get("authRequired", False)
        except Exception as e:
            pass

        # Store network requests
        result["network_requests"] = {
            "requests": captured_requests[:20],  # Limit to first 20
            "responses": captured_responses[:20],
        }

        # Save HTML dump
        try:
            html_content = await page.content()
            dump_file = f"/tmp/car_{label.lower().replace('/', '_')}_dump.html"
            Path(dump_file).write_text(html_content)
            print(f"\nHTML dump saved to: {dump_file}")
        except Exception as e:
            print(f"Could not save HTML dump: {e}")

        await browser.close()

    return result


async def main():
    """Main reconnaissance flow."""
    print("\n" + "="*70)
    print("CAR/SICAR PORTAL RECONNAISSANCE")
    print("="*70)

    results = []

    # Recon both portals
    urls = [
        ("https://consultapublica.car.gov.br/", "consultapublica.car.gov.br"),
        ("https://www.car.gov.br/", "www.car.gov.br"),
    ]

    for url, label in urls:
        result = await recon_portal(url, label)
        results.append(result)

        # Print summary for this portal
        print(f"\n--- SUMMARY: {label} ---")
        print(f"Status: {result.get('http_status', 'ERROR')}")
        print(f"Title: {result['title']}")
        print(f"HTML size: {result['html_size']} bytes")
        if result['stack_markers']:
            print(f"Stack markers: {', '.join(result['stack_markers'])}")
        if result['captcha_detected']:
            print(f"Captcha: {', '.join(result['captcha_detected'])}")
        print(f"Auth required: {result['auth_required']}")
        if result['form_fields']:
            print(f"Forms found: {len(result['form_fields'])}")
            for form in result['form_fields']:
                print(f"  - Form: {form['id']}")
                for field in form['fields']:
                    label_text = field.get('label', field['name'])
                    print(f"    • {field['type']}: {label_text}")
        if result['error']:
            print(f"Error: {result['error']}")

    # Save results summary
    summary_file = "/tmp/car_recon_summary.json"
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n\nFull results saved to: {summary_file}")

    # Decision logic
    print("\n" + "="*70)
    print("DECISION ANALYSIS")
    print("="*70)

    for result in results:
        print(f"\n{result['label']}:")

        # Scenario classification
        if result['error']:
            print("  Scenario: UNREACHABLE")
        elif result['captcha_detected']:
            if 'hcaptcha' in str(result['captcha_detected']):
                print("  Scenario: B/D (hCaptcha visible or invisible)")
            else:
                print("  Scenario: B (reCAPTCHA)")
        elif result['stack_markers']:
            print(f"  Scenario: C (SPA: {result['stack_markers'][0]})")
        elif result['auth_required']:
            print("  Scenario: E (Auth required)")
        else:
            print("  Scenario: A (Static HTML) or F (bulk dataset)")

        # Bulk dataset feasibility
        if result['http_status'] == 200:
            print("  Bulk dataset check: Need manual inspection of download endpoints")
        else:
            print("  Bulk dataset check: Portal may require special access")


if __name__ == "__main__":
    asyncio.run(main())

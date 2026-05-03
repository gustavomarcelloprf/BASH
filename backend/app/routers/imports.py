import os
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlmodel import Session

from ..database import get_session
from ..models.user import User
from ..services.importer import ImportResult, import_xlsx
from .auth import get_admin_user

router = APIRouter(prefix="/api/import", tags=["import"])


class ImportResponse(BaseModel):
    imported: int
    skipped: int
    duplicates: int
    warnings: list[str]


@router.post("/excel", response_model=ImportResponse, status_code=status.HTTP_200_OK)
def import_excel(
    file: Annotated[UploadFile, File()],
    current_user: Annotated[User, Depends(get_admin_user)],
    session: Annotated[Session, Depends(get_session)],
):
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Apenas arquivos .xlsx são aceitos.",
        )

    tmp_path = f"/tmp/dash-import-{uuid.uuid4()}.xlsx"
    try:
        content = file.file.read()
        with open(tmp_path, "wb") as f:
            f.write(content)

        result: ImportResult = import_xlsx(tmp_path, current_user.id, session)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return ImportResponse(
        imported=result.imported,
        skipped=result.skipped,
        duplicates=result.duplicates,
        warnings=result.warnings,
    )

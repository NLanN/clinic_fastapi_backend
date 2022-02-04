from db.mixin import DBMixin
from models.patient import Patient
from schemas.patient import PatientCreateRequest, PatientUpdateRequest


class PatientService(DBMixin[Patient, PatientCreateRequest, PatientUpdateRequest]):
    ...


patient_service = PatientService(Patient)

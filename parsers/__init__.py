from .linkedin import LinkedInReport, parse_linkedin_report
from .vitel import VitelReport, parse_vitel_cdr_csv

__all__ = [
    "LinkedInReport",
    "VitelReport",
    "parse_linkedin_report",
    "parse_vitel_cdr_csv",
]

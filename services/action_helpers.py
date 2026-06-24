from contextlib import contextmanager
from typing import Any
from xml.dom import minidom as mnd
from flask import request


class Sf_Xml_Parser:
    def __call__(self, xml_text: str):
        if xml_text:
            return mnd.parseString(xml_text).documentElement.tagName
        return ""


def get_pro_hst(pro_hst_str: str):
    if pro_hst_str:
        return pro_hst_str
    return "processor.health.local"


def get_host(pro_hst: str):
    if pro_hst:
        return pro_hst
    return request.headers.get("X-Forwarded-Host")


@contextmanager
def pro_hst_context(pro_hst_str: str):
    pro_hst = get_pro_hst(pro_hst_str)
    host = get_host(pro_hst)
    yield host


def get_user_data(form: Any = None):
    return request.form.get("xml_text", "").strip()
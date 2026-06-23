from xml.dom import minidom
from flask import request

def sf_xml_parser(xml_text:str):
    return minidom.parseString(xml_text).documentElement.tagName


def get_processor_host(processor_host_str:str):
    if processor_host_str:
        return processor_host_str
    return  "processor.health.local"


def get_host(processor_host:str):
    if processor_host:
        return processor_host
    return request.headers.get("X-Forwarded-Host") 
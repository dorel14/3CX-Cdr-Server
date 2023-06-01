from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import select, Session
from typing import Union, List

import os
import sys

sys.path.append(os.path.abspath("."))

from myhelpers.base import get_session

from models.tab3cxcdr import (
    call_data_records,
    call_data_records_base,
    call_data_records_create,
    call_data_records_read
)

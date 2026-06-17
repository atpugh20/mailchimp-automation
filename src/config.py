import os
from dotenv import load_dotenv

load_dotenv()
XCD_KEY = os.getenv("XCD_KEY")

MC_KEY = os.getenv("MC_KEY")
MC_SERVER = os.getenv("MC_SERVER")
MC_TEST_LIST_ID = os.getenv("MC_TEST_LIST_ID")
MC_MAIN_LIST_ID = os.getenv("MC_MAIN_LIST_ID")

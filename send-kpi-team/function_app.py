# function_app.py
import azure.functions as func
from SendToTeamsKpi import SendToTeamsKpi

app = func.FunctionApp()
app.register_functions(SendToTeamsKpi)

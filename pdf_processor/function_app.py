import azure.functions as func
import process_pdf_trigger  # Blueprint 정의된 모듈

app = func.FunctionApp()
app.register_functions(process_pdf_trigger.process_pdf_trigger)

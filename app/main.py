from fastapi import FastAPI, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict
import uvicorn
from app.services.survey_service import SurveyService
from app.models.survey_structure import SurveyStructure
from app.database import init_db
import tempfile
import os

app = FastAPI(title="Survey Application")
survey_service = None  # Se inicializará cuando se cargue la estructura


@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al iniciar la aplicación"""
    await init_db()


@app.get("/", response_class=HTMLResponse)
async def show_upload(request: Request):
    """Muestra la página de carga de estructura"""
    if not survey_service:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cargar Estructura de Encuesta</title>
            <style>
                body { 
                    font-family: Arial; 
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container { 
                    max-width: 600px; 
                    margin: auto;
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .upload-form { 
                    margin: 20px 0;
                    padding: 20px;
                    border: 2px dashed #ccc;
                    border-radius: 4px;
                }
                .download-template { 
                    margin: 20px 0;
                    text-align: center;
                }
                input[type="file"] {
                    display: block;
                    margin: 10px 0;
                }
                button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
                a {
                    color: #2196F3;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Configuración de Encuesta</h1>
                <div class="upload-form">
                    <h2>Cargar Estructura</h2>
                    <form action="/upload" method="post" enctype="multipart/form-data">
                        <input type="file" name="file" accept=".xlsx" required>
                        <button type="submit">Iniciar Encuesta</button>
                    </form>
                </div>
                <div class="download-template">
                    <h2>¿No tienes un archivo de encuesta?</h2>
                    <a href="/template" download>Descargar plantilla Excel</a>
                </div>
            </div>
        </body>
        </html>
        """
    return await survey_service.get_survey_page(request, 0)


@app.post("/upload")
async def upload_structure(file: UploadFile = File(...)):
    """Procesa el archivo Excel subido"""
    global survey_service
    
    # Guardar el archivo temporalmente
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        contents = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(contents)
        print(f"Archivo guardado temporalmente en: {temp_path}")
        
        # Cargar la estructura
        structure = SurveyStructure(temp_path)
        structure.validate_structure()
        print("Estructura validada correctamente.")
        
        # Inicializar el servicio de encuesta
        survey_service = SurveyService(structure)
        print("SurveyService inicializado correctamente.")
        
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Estructura cargada exitosamente</h1>
            <p>La encuesta ha sido inicializada. Puedes comenzar a responder.</p>
            <a href="/">Ir al inicio</a>
        </body>
        </html>
        """)
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Error</h1>
            <p>{str(e)}</p>
            <a href="/">Volver</a>
        </body>
        </html>
        """, status_code=400)
    finally:
        os.remove(temp_path)
        os.rmdir(temp_dir)


@app.get("/template")
async def get_template():
    """Descarga la plantilla Excel"""
    template_path = SurveyStructure.get_excel_template()
    return FileResponse(
        template_path,
        filename="survey_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.post("/next")
async def next_page(
    current_page: int = Form(...),
    action: str = Form(...),
    request: Request = None
):
    """Endpoint para procesar las respuestas y navegar entre páginas"""
    if not survey_service:
        return {"error": "No se ha cargado la estructura de la encuesta"}
        
    form_data = await request.form()
    next_action, next_page = await survey_service.process_responses(current_page, action, dict(form_data))
    
    if next_action == "results":
        return await survey_service.show_results()
    else:
        return await survey_service.get_survey_page(request, next_page)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

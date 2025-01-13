from fastapi.responses import HTMLResponse
from fastapi import Request
from jinja2 import Environment, FileSystemLoader
from typing import Dict, Tuple
from ..models.survey import Survey
from ..models.survey_structure import SurveyStructure
from ..models.db_models import Survey as DBSurvey, Response as DBResponse
from .llm_service import LLMService
from ..database import AsyncSessionLocal
import os
import json


class SurveyService:
    def __init__(self, structure: SurveyStructure = None):
        """Inicializa el servicio con una estructura de encuesta opcional"""
        self.llm_service = LLMService()

        # Configurar Jinja2 para los templates
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))

        # Inicializar la encuesta con la estructura si se proporciona
        if structure:
            self.survey = Survey(structure)
        else:
            self.survey = None

    async def get_survey_page(self, request: Request, page: int = 0) -> HTMLResponse:
        """Renderiza una página del formulario"""
        if not self.survey:
            raise ValueError("No se ha cargado la estructura de la encuesta")

        if page >= len(self.survey.pages):
            return await self.show_results()

        template = self.env.get_template('survey.html')
        html = template.render(
            page=page,
            total_pages=len(self.survey.pages),
            current_questions=self.survey.pages[page],
            is_last_page=(page == len(self.survey.pages) - 1),
            title=self.survey.title,
            description=self.survey.description
        )

        return HTMLResponse(content=html)

    async def process_responses(self, current_page: int, action: str, form_data: Dict) -> Tuple[str, int]:
        """Procesa las respuestas y determina la siguiente página"""
        if not self.survey:
            raise ValueError("No se ha cargado la estructura de la encuesta")

        page_responses = {
            k: v for k, v in form_data.items()
            if k.startswith('q')
        }

        if page_responses:
            self.survey.add_responses(str(current_page), page_responses)

        if action == "prev":
            next_page = max(0, current_page - 1)
            return "survey", next_page
        elif action == "next":
            return "survey", current_page + 1
        else:  # action == "finish"
            return "results", 0

    async def save_survey_results(self, stats: Dict, interpretation: str):
        """Guarda los resultados de la encuesta en la base de datos"""
        async with AsyncSessionLocal() as session:
            db_survey = DBSurvey(
                overall_score=stats['overall_score'],
                interpretation=interpretation,
                category_averages=json.dumps(stats['category_averages']),
                response_distribution=json.dumps(stats['response_distribution'])
            )
            session.add(db_survey)
            await session.flush()

            for idx, score in stats['all_responses']:
                category = next(
                    (cat for cat, indices in self.survey.question_categories.items() if idx in indices),
                    None
                )

                db_response = DBResponse(
                    survey_id=db_survey.id,
                    question_idx=idx,
                    score=score,
                    category=category
                )
                session.add(db_response)

            await session.commit()

    async def show_results(self) -> HTMLResponse:
        """Muestra los resultados de la encuesta con dashboard"""
        if not self.survey:
            raise ValueError("No se ha cargado la estructura de la encuesta")

        stats = self.survey.calculate_statistics()
        interpretation = await self.llm_service.get_interpretation(stats)

        # Guardar resultados en la base de datos
        await self.save_survey_results(stats, interpretation)

        # Renderizar resultados
        template = self.env.get_template('results.html')
        html = template.render(
            stats=stats,
            interpretation=interpretation,
            questions=self.survey.questions,
            question_categories=self.survey.question_categories,
            title=self.survey.title
        )

        self.survey.clear_responses()
        return HTMLResponse(content=html)


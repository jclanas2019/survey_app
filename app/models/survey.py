# app/models/survey.py
from typing import Dict, List
import statistics
from .survey_structure import SurveyStructure

class Survey:
    def __init__(self, structure: SurveyStructure):
        """Inicializa una encuesta con la estructura proporcionada"""
        self.structure = structure
        self.questions = structure.questions
        self.question_categories = structure.categories
        self.questions_per_page = structure.questions_per_page
        self.title = structure.title
        self.description = structure.description
        
        # Calcular las páginas
        self.pages = self.structure.get_pages()
        
        # Inicializar respuestas
        self.responses: Dict[str, Dict[str, str]] = {}

    def add_responses(self, page: str, responses: Dict[str, str]) -> None:
        """Agrega respuestas para una página específica"""
        self.responses[page] = responses

    def clear_responses(self) -> None:
        """Limpia todas las respuestas almacenadas"""
        self.responses.clear()

    def calculate_statistics(self) -> Dict:
        """Calcula las estadísticas basadas en las respuestas"""
        all_responses = []
        category_scores = {category: [] for category in self.question_categories}
        
        # Recolectar todas las respuestas
        for page_num in sorted(self.responses.keys()):
            page_responses = self.responses[page_num]
            page_idx = int(page_num)
            
            for q_key, answer in page_responses.items():
                q_idx = int(q_key.split('_')[1])
                absolute_idx = page_idx * self.questions_per_page + q_idx
                score = int(answer)
                all_responses.append((absolute_idx, score))
                
                # Agregar a categorías correspondientes
                for category, indices in self.question_categories.items():
                    if absolute_idx in indices:
                        category_scores[category].append(score)
        
        # Calcular promedios por categoría
        category_averages = {
            category: round(statistics.mean(scores), 2)
            for category, scores in category_scores.items()
            if scores
        }
        
        # Calcular distribución de respuestas
        response_distribution = {i: 0 for i in range(1, 6)}
        for _, score in all_responses:
            response_distribution[score] += 1
        
        # Calcular estadísticas generales
        overall_score = round(statistics.mean([score for _, score in all_responses]), 2)
        total_responses = len(all_responses)
        highest_category = max(category_averages.items(), key=lambda x: x[1])[0] if category_averages else None
        
        return {
            'category_averages': category_averages,
            'response_distribution': response_distribution,
            'all_responses': sorted(all_responses),
            'overall_score': overall_score,
            'total_responses': total_responses,
            'highest_category': highest_category
        }
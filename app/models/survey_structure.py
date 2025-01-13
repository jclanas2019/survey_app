# app/models/survey_structure.py
from typing import Dict, List
import pandas as pd
import json


class SurveyStructure:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.questions = []
        self.categories = {}
        self.questions_per_page = 5
        self.title = ""
        self.description = ""
        self.load_from_excel()

    def load_from_excel(self):
        """Carga la estructura de la encuesta desde un archivo Excel"""
        try:
            df_config = pd.read_excel(self.excel_path, sheet_name='Configuración')
            df_questions = pd.read_excel(self.excel_path, sheet_name='Preguntas')
            df_categories = pd.read_excel(self.excel_path, sheet_name='Categorías')

            config_dict = df_config.set_index('Parámetro')['Valor'].to_dict()
            self.title = config_dict.get('Título', 'Encuesta')
            self.description = config_dict.get('Descripción', '')
            self.questions_per_page = int(config_dict.get('Preguntas por página', 5))

            self.questions = df_questions['Pregunta'].tolist()

            for _, row in df_categories.iterrows():
                category = row['Categoría']
                question_indices = json.loads(row['Índices de preguntas'])
                self.categories[category] = question_indices

        except Exception as e:
            raise ValueError(f"Error al cargar el archivo Excel: {str(e)}")

    def validate_structure(self) -> bool:
        """Valida que la estructura de la encuesta sea correcta"""
        if not self.questions:
            raise ValueError("No hay preguntas definidas en la encuesta")

        if not self.categories:
            raise ValueError("No hay categorías definidas en la encuesta")

        all_indices = []
        for indices in self.categories.values():
            all_indices.extend(indices)
            for idx in indices:
                if idx < 0 or idx >= len(self.questions):
                    raise ValueError(f"Índice de pregunta inválido: {idx}")

        if len(set(all_indices)) != len(self.questions):
            raise ValueError("No todas las preguntas están asignadas a categorías")

        return True

    def get_pages(self) -> List[List[str]]:
        """
        Divide las preguntas en páginas según la configuración.
        """
        return [
            self.questions[i:i + self.questions_per_page]
            for i in range(0, len(self.questions), self.questions_per_page)
        ]

    def to_dict(self) -> Dict:
        """Convierte la estructura a un diccionario"""
        return {
            'title': self.title,
            'description': self.description,
            'questions': self.questions,
            'categories': self.categories,
            'questions_per_page': self.questions_per_page
        }

    @classmethod
    def get_excel_template(cls) -> str:
        """Genera un archivo Excel de plantilla"""
        # Crear un escritor de Excel
        output_path = 'survey_template.xlsx'
        writer = pd.ExcelWriter(output_path, engine='openpyxl')

        # Hoja de Configuración
        df_config = pd.DataFrame({
            'Parámetro': ['Título', 'Descripción', 'Preguntas por página'],
            'Valor': ['Mi Encuesta', 'Descripción de la encuesta', 5]
        })
        df_config.to_excel(writer, sheet_name='Configuración', index=False)

        # Hoja de Preguntas
        df_questions = pd.DataFrame({
            'Pregunta': ['¿Ejemplo de pregunta 1?', '¿Ejemplo de pregunta 2?']
        })
        df_questions.to_excel(writer, sheet_name='Preguntas', index=False)

        # Hoja de Categorías
        df_categories = pd.DataFrame({
            'Categoría': ['Categoría 1', 'Categoría 2'],
            'Índices de preguntas': ['[0]', '[1]']
        })
        df_categories.to_excel(writer, sheet_name='Categorías', index=False)

        writer.close()
        return output_path

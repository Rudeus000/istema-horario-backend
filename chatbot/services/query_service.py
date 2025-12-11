"""
Servicio de Consultas a la Base de Datos
Traduce intenciones estructuradas en consultas SQL/ORM y retorna resultados
"""
from typing import Dict, List, Optional
from datetime import datetime, time
from django.db.models import Q, Count
from django.utils import timezone

from apps.academic_setup.models import (
    EspaciosFisicos, TiposEspacio, PeriodoAcademico,
    Materias, Carrera, UnidadAcademica
)
from apps.users.models import Docentes
from apps.scheduling.models import (
    HorariosAsignados, BloquesHorariosDefinicion, 
    DisponibilidadDocentes, Grupos
)
from .nlp_service import IntentType, NLPService


class QueryService:
    """Servicio para ejecutar consultas basadas en intenciones"""
    
    def __init__(self):
        self.nlp_service = NLPService()
    
    def execute_query(
        self, 
        intent_data: Dict,
        user=None,
        user_role: str = 'Usuario'
    ) -> Dict:
        """
        Ejecuta una consulta basada en la intención procesada
        
        Args:
            intent_data: Dict con intent, entities, confidence, original_message
            user: Usuario de Django (opcional)
            user_role: Rol del usuario
            
        Returns:
            Dict con:
                - success: bool
                - data: List/Dict con los resultados
                - message: str mensaje de respuesta al usuario
                - query_type: str tipo de consulta ejecutada
        """
        intent = intent_data.get('intent')
        entities = intent_data.get('entities', {})
        
        # Asegurar que intent sea un IntentType enum
        if isinstance(intent, str):
            try:
                intent = IntentType(intent.lower().strip())
            except ValueError:
                # Buscar el enum correspondiente por valor
                for intent_type in IntentType:
                    if intent_type.value == intent.lower().strip():
                        intent = intent_type
                        break
                else:
                    intent = IntentType.DESCONOCIDO
        
        # Personalizar entidades según el rol del usuario
        if user_role == 'Docente' and user and hasattr(user, 'perfil_docente'):
            # Si un docente pregunta sobre "mi horario", usar su perfil
            original_msg = intent_data.get('original_message', '').lower()
            if 'mi' in original_msg or 'yo' in original_msg or 'mío' in original_msg:
                docente = user.perfil_docente
                entities['nombre'] = f"{docente.nombres} {docente.apellidos}"
                entities['nombre_docente'] = entities['nombre']
        
        try:
            if intent == IntentType.AULAS_DISPONIBLES:
                return self._query_aulas_disponibles(entities)
            
            elif intent == IntentType.DOCENTES_DISPONIBLES:
                return self._query_docentes_disponibles(entities)
            
            elif intent == IntentType.HORARIOS_DOCENTE:
                return self._query_horarios_docente(entities)
            
            elif intent == IntentType.HORARIOS_AULA:
                return self._query_horarios_aula(entities)
            
            elif intent == IntentType.TIPOS_AULAS:
                return self._query_tipos_aulas()
            
            elif intent == IntentType.BUSCAR_DOCENTE:
                return self._query_buscar_docente(entities)
            
            elif intent == IntentType.BUSCAR_AULA:
                return self._query_buscar_aula(entities)
            
            elif intent == IntentType.CONFLICTOS:
                return self._query_conflictos()
            
            elif intent == IntentType.HUECOS_HORARIOS:
                return self._query_huecos_horarios(entities)
            
            elif intent == IntentType.HUECOS_DOCENTE:
                return self._query_huecos_docente(entities)
            
            elif intent == IntentType.HUECOS_AULA:
                return self._query_huecos_aula(entities)
            
            elif intent == IntentType.HUECOS_GRUPO:
                return self._query_huecos_grupo(entities)
            
            elif intent == IntentType.COMPARAR_DOCENTES:
                return self._query_comparar_docentes(entities)
            
            elif intent == IntentType.COMPARAR_AULAS:
                return self._query_comparar_aulas(entities)
            
            elif intent == IntentType.CARGA_DOCENTE:
                return self._query_carga_docente(entities)
            
            elif intent == IntentType.CARGA_AULA:
                return self._query_carga_aula(entities)
            
            elif intent == IntentType.ESTADISTICAS_PERIODO:
                return self._query_estadisticas_periodo(entities)
            
            elif intent == IntentType.BUSCAR_MATERIA:
                return self._query_buscar_materia(entities)
            
            elif intent == IntentType.BUSCAR_CARRERA:
                return self._query_buscar_carrera(entities)
            
            elif intent == IntentType.MATERIAS_CARRERA:
                return self._query_materias_carrera(entities)
            
            elif intent == IntentType.GRUPOS_CARRERA:
                return self._query_grupos_carrera(entities)
            
            elif intent == IntentType.HORARIOS_GRUPO:
                return self._query_horarios_grupo(entities)
            
            elif intent == IntentType.ANALISIS_COMPLETO:
                return self._query_analisis_completo(entities)
            
            elif intent == IntentType.SALUDO:
                # La IA generará el mensaje
                return {
                    'success': True,
                    'data': None,
                    'message': '',  # Vacío - la IA lo generará
                    'query_type': 'saludo'
                }
            
            elif intent == IntentType.AYUDA:
                # La IA generará el mensaje con ejemplos
                return {
                    'success': True,
                    'data': None,
                    'message': '',  # Vacío - la IA lo generará
                    'query_type': 'ayuda'
                }
            
            elif intent == IntentType.DESPEDIDA:
                # La IA generará el mensaje
                return {
                    'success': True,
                    'data': None,
                    'message': '',  # Vacío - la IA lo generará
                    'query_type': 'despedida'
                }
            
            else:
                # La IA generará el mensaje de error/desconocido
                return {
                    'success': False,
                    'data': None,
                    'message': '',  # Vacío - la IA lo generará
                    'query_type': 'desconocido'
                }
        
        except Exception as e:
            return {
                'success': False,
                'data': None,
                'message': f'Hubo un error al procesar tu consulta: {str(e)}',
                'query_type': 'error'
            }
    
    def _query_aulas_disponibles(self, entities: Dict) -> Dict:
        """Consulta aulas disponibles para un día y hora específicos"""
        dia = entities.get('dia')
        hora = entities.get('hora')
        turno = entities.get('turno')
        # Aceptar tanto tipo_aula como tipo_espacio (la IA puede usar cualquiera)
        tipo_aula = entities.get('tipo_aula') or entities.get('tipo_espacio')
        periodo_id = entities.get('periodo_id')
        
        # Obtener período activo si no se especifica
        if not periodo_id:
            periodo_activo = PeriodoAcademico.objects.filter(
                fecha_inicio__lte=timezone.now().date(),
                fecha_fin__gte=timezone.now().date()
            ).first()
            if periodo_activo:
                periodo_id = periodo_activo.periodo_id
        
        if not periodo_id:
            return {
                'success': False,
                'data': None,
                'message': 'No se encontró un período académico activo. Por favor especifica un período.',
                'query_type': 'aulas_disponibles'
            }
        
        # Obtener todas las aulas
        aulas_query = EspaciosFisicos.objects.all()
        
        # Filtrar por tipo si se especifica
        # La IA ya normalizó el tipo_espacio a "Laboratorio" o "Teoria", usar directamente
        if tipo_aula:
            tipo_aula_normalizado = tipo_aula.strip()
            print(f"🔍 Filtrando por tipo_espacio (valor exacto de IA): '{tipo_aula_normalizado}'")
            
            # La IA ya normalizó todo, solo buscar exactamente lo que dice
            # El algoritmo NO interpreta, solo ejecuta el comando exacto
            aulas_query = aulas_query.filter(
                tipo_espacio__nombre_tipo_espacio__icontains=tipo_aula_normalizado
            )
            
            count_resultado = aulas_query.count()
            print(f"   → Resultados después del filtro: {count_resultado} espacios")
            
            # Si no hay resultados, log adicional para debug
            if count_resultado == 0:
                # Ver qué tipos de espacios existen
                tipos_existentes = TiposEspacio.objects.values_list('nombre_tipo_espacio', flat=True)
                print(f"   ⚠️  No se encontraron resultados. Tipos existentes en BD: {list(tipos_existentes)}")
                print(f"   💡 La IA debería normalizar '{tipo_aula_normalizado}' a uno de los tipos existentes")
        
        # Obtener aulas ocupadas
        aulas_ocupadas_query = HorariosAsignados.objects.filter(
            periodo_id=periodo_id,
            estado__in=['Programado', 'Confirmado']
        )
        
        if dia:
            aulas_ocupadas_query = aulas_ocupadas_query.filter(dia_semana=dia)
        
        if hora:
            try:
                hora_time = datetime.strptime(hora, '%H:%M').time()
                bloques_ocupados = BloquesHorariosDefinicion.objects.filter(
                    hora_inicio__lte=hora_time,
                    hora_fin__gt=hora_time
                )
                if bloques_ocupados.exists():
                    aulas_ocupadas_query = aulas_ocupadas_query.filter(
                        bloque_horario__in=bloques_ocupados
                    )
            except ValueError:
                pass
        
        if turno:
            aulas_ocupadas_query = aulas_ocupadas_query.filter(
                bloque_horario__turno=turno
            )
        
        aulas_ocupadas_ids = aulas_ocupadas_query.values_list('espacio_id', flat=True).distinct()
        
        # Aulas disponibles = todas las aulas - aulas ocupadas
        aulas_disponibles = aulas_query.exclude(espacio_id__in=aulas_ocupadas_ids)
        
        # Preparar respuesta
        aulas_data = []
        for aula in aulas_disponibles[:20]:  # Limitar a 20 resultados
            aulas_data.append({
                'id': aula.espacio_id,
                'nombre': aula.nombre_espacio,
                'tipo': aula.tipo_espacio.nombre_tipo_espacio,
                'capacidad': aula.capacidad,
                'ubicacion': aula.ubicacion,
            })
        
        # Mensaje de respuesta
        # NO generar mensaje predefinido - la IA lo generará en personalized_message
        # El mensaje será sobrescrito por el mensaje personalizado de la IA en views.py
        return {
            'success': True,
            'data': aulas_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'aulas_disponibles',
            'count': aulas_disponibles.count()
        }
    
    def _query_docentes_disponibles(self, entities: Dict) -> Dict:
        """Consulta docentes disponibles (libres) para un día y hora específicos"""
        dia = entities.get('dia')
        hora = entities.get('hora')
        turno = entities.get('turno')
        periodo_id = entities.get('periodo_id')
        
        # Obtener período activo si no se especifica
        if not periodo_id:
            periodo_activo = PeriodoAcademico.objects.filter(
                fecha_inicio__lte=timezone.now().date(),
                fecha_fin__gte=timezone.now().date()
            ).first()
            if periodo_activo:
                periodo_id = periodo_activo.periodo_id
        
        if not periodo_id:
            return {
                'success': False,
                'data': None,
                'message': 'No se encontró un período académico activo.',
                'query_type': 'docentes_disponibles'
            }
        
        # Obtener docentes ocupados
        docentes_ocupados_query = HorariosAsignados.objects.filter(
            periodo_id=periodo_id,
            estado__in=['Programado', 'Confirmado']
        )
        
        if dia:
            docentes_ocupados_query = docentes_ocupados_query.filter(dia_semana=dia)
        
        if hora:
            try:
                hora_time = datetime.strptime(hora, '%H:%M').time()
                bloques_ocupados = BloquesHorariosDefinicion.objects.filter(
                    hora_inicio__lte=hora_time,
                    hora_fin__gt=hora_time
                )
                if bloques_ocupados.exists():
                    docentes_ocupados_query = docentes_ocupados_query.filter(
                        bloque_horario__in=bloques_ocupados
                    )
            except ValueError:
                pass
        
        if turno:
            docentes_ocupados_query = docentes_ocupados_query.filter(
                bloque_horario__turno=turno
            )
        
        docentes_ocupados_ids = docentes_ocupados_query.values_list('docente_id', flat=True).distinct()
        
        # Docentes disponibles = todos los docentes - docentes ocupados
        docentes_disponibles = Docentes.objects.exclude(docente_id__in=docentes_ocupados_ids)
        
        # Preparar respuesta
        docentes_data = []
        for docente in docentes_disponibles[:20]:
            nombre_completo = f"{docente.nombres} {docente.apellidos}"
            docentes_data.append({
                'id': docente.docente_id,
                'nombre': nombre_completo,
                'codigo': docente.codigo_docente,
                'email': docente.email,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': docentes_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'docentes_disponibles',
            'count': docentes_disponibles.count()
        }
    
    def _query_horarios_docente(self, entities: Dict) -> Dict:
        """Consulta horarios de un docente específico"""
        nombre_docente = entities.get('nombre') or entities.get('nombre_docente')
        
        if not nombre_docente:
            return {
                'success': False,
                'data': None,
                'message': 'Por favor especifica el nombre del docente. Ejemplo: "¿Qué horarios tiene el docente Juan Pérez?"',
                'query_type': 'horarios_docente'
            }
        
        # Buscar docente
        docentes = Docentes.objects.filter(
            Q(nombres__icontains=nombre_docente.split()[0]) |
            Q(apellidos__icontains=nombre_docente) |
            Q(codigo_docente__icontains=nombre_docente)
        )
        
        if not docentes.exists():
            return {
                'success': False,
                'data': None,
                'message': f'No se encontró ningún docente con el nombre "{nombre_docente}".',
                'query_type': 'horarios_docente'
            }
        
        docente = docentes.first()
        
        # Obtener horarios
        horarios = HorariosAsignados.objects.filter(
            docente=docente,
            estado__in=['Programado', 'Confirmado']
        ).select_related('bloque_horario', 'espacio', 'materia', 'grupo')
        
        horarios_data = []
        dias_nombres = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        
        for horario in horarios:
            horarios_data.append({
                'dia': dias_nombres.get(horario.dia_semana),
                'hora_inicio': horario.bloque_horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.bloque_horario.hora_fin.strftime('%H:%M'),
                'aula': horario.espacio.nombre_espacio,
                'materia': horario.materia.nombre_materia if horario.materia else 'N/A',
                'grupo': horario.grupo.codigo_grupo,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': horarios_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'horarios_docente'
        }
    
    def _query_horarios_aula(self, entities: Dict) -> Dict:
        """Consulta horarios de un aula específica"""
        nombre_aula = entities.get('nombre') or entities.get('nombre_aula')
        
        if not nombre_aula:
            return {
                'success': False,
                'data': None,
                'message': 'Por favor especifica el nombre del aula. Ejemplo: "¿Qué horarios tiene el aula A101?"',
                'query_type': 'horarios_aula'
            }
        
        # Buscar aula
        aulas = EspaciosFisicos.objects.filter(
            nombre_espacio__icontains=nombre_aula
        )
        
        if not aulas.exists():
            return {
                'success': False,
                'data': None,
                'message': f'No se encontró ningún aula con el nombre "{nombre_aula}".',
                'query_type': 'horarios_aula'
            }
        
        aula = aulas.first()
        
        # Obtener horarios
        horarios = HorariosAsignados.objects.filter(
            espacio=aula,
            estado__in=['Programado', 'Confirmado']
        ).select_related('bloque_horario', 'docente', 'materia', 'grupo')
        
        horarios_data = []
        dias_nombres = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 
                       5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        
        for horario in horarios:
            horarios_data.append({
                'dia': dias_nombres.get(horario.dia_semana),
                'hora_inicio': horario.bloque_horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.bloque_horario.hora_fin.strftime('%H:%M'),
                'docente': f"{horario.docente.nombres} {horario.docente.apellidos}",
                'materia': horario.materia.nombre_materia if horario.materia else 'N/A',
                'grupo': horario.grupo.codigo_grupo,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': horarios_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'horarios_aula'
        }
    
    def _query_tipos_aulas(self) -> Dict:
        """Consulta todos los tipos de aulas disponibles"""
        tipos = TiposEspacio.objects.all().annotate(
            total_aulas=Count('espacios')
        )
        
        tipos_data = []
        for tipo in tipos:
            tipos_data.append({
                'id': tipo.tipo_espacio_id,
                'nombre': tipo.nombre_tipo_espacio,
                'descripcion': tipo.descripcion,
                'total_aulas': tipo.total_aulas,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': tipos_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'tipos_aulas'
        }
    
    def _query_buscar_docente(self, entities: Dict) -> Dict:
        """Busca un docente por nombre"""
        nombre = entities.get('nombre') or entities.get('nombre_docente')
        
        if not nombre:
            return {
                'success': False,
                'data': None,
                'message': 'Por favor especifica el nombre del docente a buscar.',
                'query_type': 'buscar_docente'
            }
        
        docentes = Docentes.objects.filter(
            Q(nombres__icontains=nombre) |
            Q(apellidos__icontains=nombre) |
            Q(codigo_docente__icontains=nombre)
        )[:10]
        
        docentes_data = []
        for docente in docentes:
            docentes_data.append({
                'id': docente.docente_id,
                'nombre': f"{docente.nombres} {docente.apellidos}",
                'codigo': docente.codigo_docente,
                'email': docente.email,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': docentes_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'buscar_docente'
        }
    
    def _query_buscar_aula(self, entities: Dict) -> Dict:
        """Busca un aula por nombre"""
        nombre = entities.get('nombre') or entities.get('nombre_aula')
        
        if not nombre:
            return {
                'success': False,
                'data': None,
                'message': 'Por favor especifica el nombre del aula a buscar.',
                'query_type': 'buscar_aula'
            }
        
        aulas = EspaciosFisicos.objects.filter(
            nombre_espacio__icontains=nombre
        )[:10]
        
        aulas_data = []
        for aula in aulas:
            aulas_data.append({
                'id': aula.espacio_id,
                'nombre': aula.nombre_espacio,
                'tipo': aula.tipo_espacio.nombre_tipo_espacio,
                'capacidad': aula.capacidad,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': aulas_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'buscar_aula'
        }
    
    def _query_conflictos(self) -> Dict:
        """Consulta conflictos de horarios en el sistema"""
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {
                'success': False,
                'data': None,
                'message': 'No hay período activo para analizar conflictos.',
                'query_type': 'conflictos'
            }
        
        conflictos = []
        
        # Detectar conflictos: mismo docente, mismo bloque, diferentes lugares
        horarios_docentes = HorariosAsignados.objects.filter(
            periodo=periodo_activo,
            estado__in=['Programado', 'Confirmado']
        ).values('docente', 'dia_semana', 'bloque_horario').annotate(
            count=Count('horario_id')
        ).filter(count__gt=1)
        
        for conflicto in horarios_docentes:
            detalles = HorariosAsignados.objects.filter(
                periodo=periodo_activo,
                docente_id=conflicto['docente'],
                dia_semana=conflicto['dia_semana'],
                bloque_horario_id=conflicto['bloque_horario'],
                estado__in=['Programado', 'Confirmado']
            )
            
            docente = detalles.first().docente
            bloque = detalles.first().bloque_horario
            
            conflictos.append({
                'tipo': 'docente_duplicado',
                'docente': f"{docente.nombres} {docente.apellidos}",
                'dia': dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(conflicto['dia_semana']),
                'bloque': bloque.nombre_bloque,
                'detalle': f"Docente tiene {conflicto['count']} clases asignadas en el mismo horario"
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': conflictos,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'conflictos',
            'count': len(conflictos)
        }
    
    def _query_huecos_horarios(self, entities: Dict) -> Dict:
        """Detecta huecos libres en los horarios"""
        dia = entities.get('dia')
        turno = entities.get('turno')
        
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'huecos_horarios'}
        
        bloques_query = BloquesHorariosDefinicion.objects.all()
        if dia:
            bloques_query = bloques_query.filter(dia_semana=dia)
        if turno:
            bloques_query = bloques_query.filter(turno=turno)
        
        horarios = HorariosAsignados.objects.filter(
            periodo=periodo_activo,
            estado__in=['Programado', 'Confirmado']
        )
        
        if dia:
            horarios = horarios.filter(dia_semana=dia)
        
        bloques_ocupados_ids = horarios.values_list('bloque_horario_id', flat=True).distinct()
        bloques_libres = bloques_query.exclude(bloque_def_id__in=bloques_ocupados_ids)
        
        huecos_data = []
        for bloque in bloques_libres:
            aulas_ocupadas = horarios.filter(bloque_horario=bloque).values_list('espacio_id', flat=True).distinct()
            total_aulas = EspaciosFisicos.objects.count()
            aulas_libres = total_aulas - len(aulas_ocupadas)
            
            docentes_ocupados = horarios.filter(bloque_horario=bloque).values_list('docente_id', flat=True).distinct()
            total_docentes = Docentes.objects.count()
            docentes_libres = total_docentes - len(docentes_ocupados)
            
            huecos_data.append({
                'dia': dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(bloque.dia_semana),
                'bloque': bloque.nombre_bloque,
                'hora_inicio': bloque.hora_inicio.strftime('%H:%M'),
                'hora_fin': bloque.hora_fin.strftime('%H:%M'),
                'turno': bloque.get_turno_display(),
                'aulas_libres': aulas_libres,
                'docentes_libres': docentes_libres,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {
            'success': True,
            'data': huecos_data,
            'message': '',  # Vacío - la IA proporcionará el mensaje
            'query_type': 'huecos_horarios',
            'count': len(huecos_data)
        }
    
    def _query_huecos_docente(self, entities: Dict) -> Dict:
        """Detecta huecos en el horario de un docente específico"""
        nombre_docente = entities.get('nombre') or entities.get('nombre_docente')
        
        if not nombre_docente:
            return {'success': False, 'message': 'Especifica el nombre del docente', 'data': None, 'query_type': 'huecos_docente'}
        
        docentes = Docentes.objects.filter(
            Q(nombres__icontains=nombre_docente.split()[0]) | Q(apellidos__icontains=nombre_docente)
        )
        
        if not docentes.exists():
            return {'success': False, 'message': f'Docente "{nombre_docente}" no encontrado', 'data': None, 'query_type': 'huecos_docente'}
        
        docente = docentes.first()
        
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(),
            fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'huecos_docente'}
        
        horarios_docente = HorariosAsignados.objects.filter(
            docente=docente, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values_list('dia_semana', 'bloque_horario_id')
        
        disponibilidad = DisponibilidadDocentes.objects.filter(
            docente=docente, periodo=periodo_activo, esta_disponible=True
        ).values_list('dia_semana', 'bloque_horario_id')
        
        horarios_set = set((d, b) for d, b in horarios_docente)
        disponibilidad_set = set((d, b) for d, b in disponibilidad)
        huecos_set = disponibilidad_set - horarios_set
        
        huecos_data = []
        for dia, bloque_id in huecos_set:
            try:
                bloque = BloquesHorariosDefinicion.objects.get(bloque_def_id=bloque_id)
                huecos_data.append({
                    'dia': dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(dia),
                    'bloque': bloque.nombre_bloque,
                    'hora_inicio': bloque.hora_inicio.strftime('%H:%M'),
                    'hora_fin': bloque.hora_fin.strftime('%H:%M'),
                })
            except BloquesHorariosDefinicion.DoesNotExist:
                continue
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': huecos_data, 'message': '', 'query_type': 'huecos_docente'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_huecos_aula(self, entities: Dict) -> Dict:
        """Detecta huecos en el horario de un aula específica"""
        nombre_aula = entities.get('nombre') or entities.get('nombre_aula')
        
        if not nombre_aula:
            return {'success': False, 'message': 'Especifica el nombre del aula', 'data': None, 'query_type': 'huecos_aula'}
        
        aulas = EspaciosFisicos.objects.filter(nombre_espacio__icontains=nombre_aula)
        if not aulas.exists():
            return {'success': False, 'message': f'Aula "{nombre_aula}" no encontrada', 'data': None, 'query_type': 'huecos_aula'}
        
        aula = aulas.first()
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'huecos_aula'}
        
        horarios_aula = HorariosAsignados.objects.filter(
            espacio=aula, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values_list('dia_semana', 'bloque_horario_id')
        
        todos_bloques = BloquesHorariosDefinicion.objects.values_list('dia_semana', 'bloque_def_id')
        horarios_set = set((d, b) for d, b in horarios_aula)
        todos_set = set((d, b) for d, b in todos_bloques)
        huecos_set = todos_set - horarios_set
        
        huecos_data = []
        for dia, bloque_id in huecos_set:
            try:
                bloque = BloquesHorariosDefinicion.objects.get(bloque_def_id=bloque_id)
                huecos_data.append({
                    'dia': dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(dia),
                    'bloque': bloque.nombre_bloque,
                    'hora_inicio': bloque.hora_inicio.strftime('%H:%M'),
                    'hora_fin': bloque.hora_fin.strftime('%H:%M'),
                })
            except BloquesHorariosDefinicion.DoesNotExist:
                continue
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': huecos_data, 'message': '', 'query_type': 'huecos_aula'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_huecos_grupo(self, entities: Dict) -> Dict:
        """Detecta huecos en el horario de un grupo"""
        nombre_grupo = entities.get('nombre') or entities.get('codigo_grupo')
        
        if not nombre_grupo:
            return {'success': False, 'message': 'Especifica el código del grupo', 'data': None, 'query_type': 'huecos_grupo'}
        
        grupos = Grupos.objects.filter(codigo_grupo__icontains=nombre_grupo)
        if not grupos.exists():
            return {'success': False, 'message': f'Grupo "{nombre_grupo}" no encontrado', 'data': None, 'query_type': 'huecos_grupo'}
        
        grupo = grupos.first()
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'huecos_grupo'}
        
        horarios_grupo = HorariosAsignados.objects.filter(
            grupo=grupo, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values_list('dia_semana', 'bloque_horario_id')
        
        todos_bloques = BloquesHorariosDefinicion.objects.values_list('dia_semana', 'bloque_def_id')
        horarios_set = set((d, b) for d, b in horarios_grupo)
        todos_set = set((d, b) for d, b in todos_bloques)
        huecos_set = todos_set - horarios_set
        
        huecos_data = []
        for dia, bloque_id in huecos_set:
            try:
                bloque = BloquesHorariosDefinicion.objects.get(bloque_def_id=bloque_id)
                huecos_data.append({
                    'dia': dict(BloquesHorariosDefinicion.DIA_SEMANA_CHOICES).get(dia),
                    'bloque': bloque.nombre_bloque,
                    'hora_inicio': bloque.hora_inicio.strftime('%H:%M'),
                    'hora_fin': bloque.hora_fin.strftime('%H:%M'),
                })
            except BloquesHorariosDefinicion.DoesNotExist:
                continue
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': huecos_data, 'message': '', 'query_type': 'huecos_grupo'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_comparar_docentes(self, entities: Dict) -> Dict:
        """Compara carga horaria entre docentes"""
        # Intentar extraer nombres del mensaje original
        message = entities.get('original_message', '').lower()
        
        # Buscar dos nombres (simple: tomar los dos primeros nombres encontrados)
        docentes_encontrados = []
        for docente in Docentes.objects.all():
            nombre_completo = f"{docente.nombres} {docente.apellidos}".lower()
            if any(palabra in message for palabra in nombre_completo.split()):
                docentes_encontrados.append(docente)
        
        if len(docentes_encontrados) < 2:
            return {'success': False, 'message': 'Especifica dos docentes para comparar', 'data': None, 'query_type': 'comparar_docentes'}
        
        docente1, docente2 = docentes_encontrados[0], docentes_encontrados[1]
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'comparar_docentes'}
        
        horarios1 = HorariosAsignados.objects.filter(
            docente=docente1, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).count()
        
        horarios2 = HorariosAsignados.objects.filter(
            docente=docente2, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).count()
        
        comparacion = {
            'docente1': {
                'nombre': f"{docente1.nombres} {docente1.apellidos}",
                'clases_asignadas': horarios1,
                'max_horas_semanales': docente1.max_horas_semanales,
            },
            'docente2': {
                'nombre': f"{docente2.nombres} {docente2.apellidos}",
                'clases_asignadas': horarios2,
                'max_horas_semanales': docente2.max_horas_semanales,
            },
            'diferencia': horarios1 - horarios2
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': comparacion, 'message': '', 'query_type': 'comparar_docentes'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_comparar_aulas(self, entities: Dict) -> Dict:
        """Compara uso entre aulas"""
        nombre1 = entities.get('aula1') or entities.get('nombre1')
        nombre2 = entities.get('aula2') or entities.get('nombre2')
        
        if not nombre1 or not nombre2:
            return {'success': False, 'message': 'Especifica dos aulas para comparar', 'data': None, 'query_type': 'comparar_aulas'}
        
        aula1 = EspaciosFisicos.objects.filter(nombre_espacio__icontains=nombre1).first()
        aula2 = EspaciosFisicos.objects.filter(nombre_espacio__icontains=nombre2).first()
        
        if not aula1 or not aula2:
            return {'success': False, 'message': 'Una o ambas aulas no encontradas', 'data': None, 'query_type': 'comparar_aulas'}
        
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'comparar_aulas'}
        
        uso1 = HorariosAsignados.objects.filter(
            espacio=aula1, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).count()
        
        uso2 = HorariosAsignados.objects.filter(
            espacio=aula2, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).count()
        
        comparacion = {
            'aula1': {'nombre': aula1.nombre_espacio, 'uso': uso1},
            'aula2': {'nombre': aula2.nombre_espacio, 'uso': uso2},
            'diferencia': uso1 - uso2
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': comparacion, 'message': '', 'query_type': 'comparar_aulas'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_carga_docente(self, entities: Dict) -> Dict:
        """Consulta carga horaria de un docente"""
        nombre_docente = entities.get('nombre') or entities.get('nombre_docente')
        
        if not nombre_docente:
            return {'success': False, 'message': 'Especifica el nombre del docente', 'data': None, 'query_type': 'carga_docente'}
        
        docentes = Docentes.objects.filter(
            Q(nombres__icontains=nombre_docente.split()[0]) | Q(apellidos__icontains=nombre_docente)
        )
        
        if not docentes.exists():
            return {'success': False, 'message': f'Docente "{nombre_docente}" no encontrado', 'data': None, 'query_type': 'carga_docente'}
        
        docente = docentes.first()
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'carga_docente'}
        
        clases = HorariosAsignados.objects.filter(
            docente=docente, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        )
        
        carga = {
            'docente': f"{docente.nombres} {docente.apellidos}",
            'total_clases': clases.count(),
            'max_horas_semanales': docente.max_horas_semanales,
            'clases_por_dia': list(clases.values('dia_semana').annotate(count=Count('horario_id')).order_by('dia_semana'))
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': carga, 'message': '', 'query_type': 'carga_docente'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_carga_aula(self, entities: Dict) -> Dict:
        """Consulta uso/carga de un aula"""
        nombre_aula = entities.get('nombre') or entities.get('nombre_aula')
        
        if not nombre_aula:
            return {'success': False, 'message': 'Especifica el nombre del aula', 'data': None, 'query_type': 'carga_aula'}
        
        aulas = EspaciosFisicos.objects.filter(nombre_espacio__icontains=nombre_aula)
        if not aulas.exists():
            return {'success': False, 'message': f'Aula "{nombre_aula}" no encontrada', 'data': None, 'query_type': 'carga_aula'}
        
        aula = aulas.first()
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'carga_aula'}
        
        clases = HorariosAsignados.objects.filter(
            espacio=aula, periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        )
        
        carga = {
            'aula': aula.nombre_espacio,
            'total_clases': clases.count(),
            'capacidad': aula.capacidad,
            'clases_por_dia': list(clases.values('dia_semana').annotate(count=Count('horario_id')).order_by('dia_semana'))
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': carga, 'message': '', 'query_type': 'carga_aula'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_estadisticas_periodo(self, entities: Dict) -> Dict:
        """Genera estadísticas completas del período"""
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'estadisticas_periodo'}
        
        total_horarios = HorariosAsignados.objects.filter(
            periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).count()
        
        total_docentes_activos = HorariosAsignados.objects.filter(
            periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values('docente').distinct().count()
        
        total_aulas_utilizadas = HorariosAsignados.objects.filter(
            periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values('espacio').distinct().count()
        
        total_grupos = HorariosAsignados.objects.filter(
            periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values('grupo').distinct().count()
        
        distribucion_dias = HorariosAsignados.objects.filter(
            periodo=periodo_activo, estado__in=['Programado', 'Confirmado']
        ).values('dia_semana').annotate(total=Count('horario_id')).order_by('dia_semana')
        
        estadisticas = {
            'periodo': periodo_activo.nombre_periodo,
            'total_clases': total_horarios,
            'docentes_activos': total_docentes_activos,
            'aulas_utilizadas': total_aulas_utilizadas,
            'grupos_activos': total_grupos,
            'distribucion_dias': list(distribucion_dias),
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': estadisticas, 'message': '', 'query_type': 'estadisticas_periodo'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_buscar_materia(self, entities: Dict) -> Dict:
        """Busca materias por nombre o código"""
        nombre = entities.get('nombre') or entities.get('nombre_materia')
        
        if not nombre:
            return {'success': False, 'message': 'Especifica el nombre de la materia', 'data': None, 'query_type': 'buscar_materia'}
        
        materias = Materias.objects.filter(
            Q(nombre_materia__icontains=nombre) | Q(codigo_materia__icontains=nombre)
        )[:10]
        
        materias_data = []
        for materia in materias:
            materias_data.append({
                'id': materia.materia_id,
                'codigo': materia.codigo_materia,
                'nombre': materia.nombre_materia,
                'creditos': materia.creditos,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': materias_data, 'message': '', 'query_type': 'buscar_materia'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_buscar_carrera(self, entities: Dict) -> Dict:
        """Busca carreras por nombre"""
        nombre = entities.get('nombre') or entities.get('nombre_carrera')
        
        if not nombre:
            return {'success': False, 'message': 'Especifica el nombre de la carrera', 'data': None, 'query_type': 'buscar_carrera'}
        
        carreras = Carrera.objects.filter(nombre_carrera__icontains=nombre)[:10]
        
        carreras_data = []
        for carrera in carreras:
            carreras_data.append({
                'id': carrera.carrera_id,
                'nombre': carrera.nombre_carrera,
                'codigo': carrera.codigo_carrera,
                'unidad': carrera.unidad.nombre_unidad if carrera.unidad else None,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': carreras_data, 'message': '', 'query_type': 'buscar_carrera'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_materias_carrera(self, entities: Dict) -> Dict:
        """Consulta materias de una carrera"""
        nombre_carrera = entities.get('nombre') or entities.get('nombre_carrera')
        
        if not nombre_carrera:
            return {'success': False, 'message': 'Especifica el nombre de la carrera', 'data': None, 'query_type': 'materias_carrera'}
        
        carreras = Carrera.objects.filter(nombre_carrera__icontains=nombre_carrera)
        if not carreras.exists():
            return {'success': False, 'message': f'Carrera "{nombre_carrera}" no encontrada', 'data': None, 'query_type': 'materias_carrera'}
        
        carrera = carreras.first()
        materias = carrera.materias.all()
        
        materias_data = []
        for materia in materias:
            materias_data.append({
                'id': materia.materia_id,
                'codigo': materia.codigo_materia,
                'nombre': materia.nombre_materia,
                'creditos': materia.creditos,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': materias_data, 'message': '', 'query_type': 'materias_carrera'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_grupos_carrera(self, entities: Dict) -> Dict:
        """Consulta grupos de una carrera"""
        nombre_carrera = entities.get('nombre') or entities.get('nombre_carrera')
        
        if not nombre_carrera:
            return {'success': False, 'message': 'Especifica el nombre de la carrera', 'data': None, 'query_type': 'grupos_carrera'}
        
        carreras = Carrera.objects.filter(nombre_carrera__icontains=nombre_carrera)
        if not carreras.exists():
            return {'success': False, 'message': f'Carrera "{nombre_carrera}" no encontrada', 'data': None, 'query_type': 'grupos_carrera'}
        
        carrera = carreras.first()
        grupos = Grupos.objects.filter(carrera=carrera)
        
        grupos_data = []
        for grupo in grupos:
            grupos_data.append({
                'id': grupo.grupo_id,
                'codigo': grupo.codigo_grupo,
                'periodo': grupo.periodo.nombre_periodo if grupo.periodo else None,
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': grupos_data, 'message': '', 'query_type': 'grupos_carrera'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_horarios_grupo(self, entities: Dict) -> Dict:
        """Consulta horarios de un grupo"""
        codigo_grupo = entities.get('nombre') or entities.get('codigo_grupo')
        
        if not codigo_grupo:
            return {'success': False, 'message': 'Especifica el código del grupo', 'data': None, 'query_type': 'horarios_grupo'}
        
        grupos = Grupos.objects.filter(codigo_grupo__icontains=codigo_grupo)
        if not grupos.exists():
            return {'success': False, 'message': f'Grupo "{codigo_grupo}" no encontrado', 'data': None, 'query_type': 'horarios_grupo'}
        
        grupo = grupos.first()
        horarios = HorariosAsignados.objects.filter(
            grupo=grupo, estado__in=['Programado', 'Confirmado']
        ).select_related('bloque_horario', 'espacio', 'materia', 'docente')
        
        horarios_data = []
        dias_nombres = {1: 'Lunes', 2: 'Martes', 3: 'Miércoles', 4: 'Jueves', 5: 'Viernes', 6: 'Sábado', 7: 'Domingo'}
        
        for horario in horarios:
            horarios_data.append({
                'dia': dias_nombres.get(horario.dia_semana),
                'hora_inicio': horario.bloque_horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.bloque_horario.hora_fin.strftime('%H:%M'),
                'aula': horario.espacio.nombre_espacio,
                'materia': horario.materia.nombre_materia if horario.materia else 'N/A',
                'docente': f"{horario.docente.nombres} {horario.docente.apellidos}",
            })
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': horarios_data, 'message': '', 'query_type': 'horarios_grupo'}  # Vacío - la IA proporcionará el mensaje
    
    def _query_analisis_completo(self, entities: Dict) -> Dict:
        """Genera un análisis completo del sistema"""
        periodo_activo = PeriodoAcademico.objects.filter(
            fecha_inicio__lte=timezone.now().date(), fecha_fin__gte=timezone.now().date()
        ).first()
        
        if not periodo_activo:
            return {'success': False, 'message': 'No hay período activo', 'data': None, 'query_type': 'analisis_completo'}
        
        # Combinar múltiples estadísticas
        estadisticas = self._query_estadisticas_periodo(entities)['data']
        conflictos = self._query_conflictos()['data']
        
        analisis = {
            'periodo': estadisticas['periodo'],
            'resumen': estadisticas,
            'conflictos': conflictos,
            'total_conflictos': len(conflictos) if conflictos else 0,
            'aulas_totales': EspaciosFisicos.objects.count(),
            'docentes_totales': Docentes.objects.count(),
            'materias_totales': Materias.objects.count(),
            'carreras_totales': Carrera.objects.count(),
        }
        
        # NO generar mensaje predefinido - la IA lo generará
        return {'success': True, 'data': analisis, 'message': '', 'query_type': 'analisis_completo'}  # Vacío - la IA proporcionará el mensaje
    
    def _get_help_message(self) -> Dict:
        """Retorna mensaje de ayuda con ejemplos"""
        ejemplos = [
            "📚 CONSULTAS BÁSICAS:",
            "• ¿Qué aulas están disponibles el lunes a las 8:00?",
            "• ¿Qué docentes están libres los martes por la tarde?",
            "• ¿Qué horarios tiene el docente Juan Pérez?",
            "• ¿Qué clases hay en el aula A101?",
            "• ¿Qué tipos de aulas hay?",
            "• Buscar docente llamado García",
            "",
            "🔍 DETECCIÓN DE HUECOS:",
            "• ¿Qué huecos hay el lunes?",
            "• ¿Qué huecos tiene el docente Juan Pérez?",
            "• ¿Qué huecos tiene el aula A101?",
            "• ¿Qué huecos tiene el grupo GR001?",
            "",
            "📊 COMPARACIONES:",
            "• Compara docentes Juan y María",
            "• Compara aulas A101 y A102",
            "• ¿Quién tiene más clases?",
            "",
            "📈 ESTADÍSTICAS Y CARGA:",
            "• ¿Cuántas clases tiene el docente Juan?",
            "• ¿Cuántas clases se dan en el aula A101?",
            "• Dame estadísticas del período",
            "• Análisis completo",
            "",
            "🎓 BÚSQUEDAS ACADÉMICAS:",
            "• Buscar materia Matemáticas",
            "• Buscar carrera Ingeniería",
            "• ¿Qué materias tiene la carrera de Ingeniería?",
            "• ¿Qué grupos tiene la carrera de Ingeniería?",
            "• ¿Qué horarios tiene el grupo GR001?",
            "",
            "⚠️ CONFLICTOS:",
            "• ¿Hay conflictos de horarios?",
        ]
        
        # NO generar mensaje predefinido - la IA lo generará con ejemplos
        return {
            'success': True,
            'data': ejemplos,
            'message': '',  # Vacío - la IA proporcionará el mensaje con ejemplos
            'query_type': 'ayuda'
        }


#apps/scheduling/serializers.py
from rest_framework import serializers
from .models import Grupos, BloquesHorariosDefinicion, DisponibilidadDocentes, HorariosAsignados, ConfiguracionRestricciones
from apps.academic_setup.serializers import MateriasSerializer, CarreraSerializer, EspaciosFisicosSerializer
from apps.users.serializers import DocentesSerializer
from apps.academic_setup.models import PeriodoAcademico, Materias, EspaciosFisicos
from apps.users.models import Docentes

class GruposSerializer(serializers.ModelSerializer):
    materias_detalle = MateriasSerializer(source='materias', many=True, read_only=True)
    carrera_detalle = CarreraSerializer(source='carrera', read_only=True)
    periodo_nombre = serializers.CharField(source='periodo.nombre_periodo', read_only=True)
    docente_asignado_directamente_nombre = serializers.SerializerMethodField()

    def get_docente_asignado_directamente_nombre(self, obj):
        if obj.docente_asignado_directamente:
            docente = obj.docente_asignado_directamente
            return f"{docente.nombres} {docente.apellidos}"
        return None

    def validate(self, data):
        print(f"[GruposSerializer] Validando datos: {data}")
        
        # Verificar restricción unique_together
        codigo_grupo = data.get('codigo_grupo')
        periodo = data.get('periodo')
        
        if codigo_grupo and periodo:
            # Excluir el grupo actual si estamos actualizando
            instance = self.instance
            queryset = Grupos.objects.filter(codigo_grupo=codigo_grupo, periodo=periodo)
            if instance:
                queryset = queryset.exclude(pk=instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'codigo_grupo': f'Ya existe un grupo con el código "{codigo_grupo}" en el período seleccionado.'
                })
        
        return data

    def create(self, validated_data):
        materias_data = validated_data.pop('materias')
        grupo = Grupos.objects.create(**validated_data)
        grupo.materias.set(materias_data)
        return grupo

    def update(self, instance, validated_data):
        materias_data = validated_data.pop('materias', None)
        
        # Actualizar campos del modelo base
        instance = super().update(instance, validated_data)

        # Actualizar la relación ManyToMany si se proporcionaron datos
        if materias_data is not None:
            instance.materias.set(materias_data)
            
        return instance

    class Meta:
        model = Grupos
        fields = ['grupo_id', 'codigo_grupo', 'materias', 'materias_detalle', 'carrera', 'carrera_detalle',
                  'periodo', 'periodo_nombre', 'numero_estudiantes_estimado', 'turno_preferente',
                  'docente_asignado_directamente', 'docente_asignado_directamente_nombre',
                  'ciclo_semestral']

class BloquesHorariosDefinicionSerializer(serializers.ModelSerializer):
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True, allow_null=True)
    turno_display = serializers.CharField(source='get_turno_display', read_only=True)

    class Meta:
        model = BloquesHorariosDefinicion
        fields = ['bloque_def_id', 'nombre_bloque', 'hora_inicio', 'hora_fin',
                  'turno', 'turno_display', 'dia_semana', 'dia_semana_display']

class DisponibilidadDocentesSerializer(serializers.ModelSerializer):
    docente_nombre = serializers.CharField(source='docente.__str__', read_only=True)
    periodo_nombre = serializers.CharField(source='periodo.nombre_periodo', read_only=True)
    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)
    bloque_horario_detalle = BloquesHorariosDefinicionSerializer(source='bloque_horario', read_only=True)
    origen_carga_display = serializers.CharField(source='get_origen_carga_display', read_only=True)


    class Meta:
        model = DisponibilidadDocentes
        fields = ['disponibilidad_id', 'docente', 'docente_nombre', 'periodo', 'periodo_nombre',
                  'dia_semana', 'dia_semana_display', 'bloque_horario', 'bloque_horario_detalle',
                  'esta_disponible', 'preferencia', 'origen_carga', 'origen_carga_display']

class HorariosAsignadosSerializer(serializers.ModelSerializer):
    # Campos para la creación/actualización, esperando IDs
    grupo = serializers.PrimaryKeyRelatedField(queryset=Grupos.objects.all())
    materia = serializers.PrimaryKeyRelatedField(queryset=Materias.objects.all())
    docente = serializers.PrimaryKeyRelatedField(queryset=Docentes.objects.all())
    espacio = serializers.PrimaryKeyRelatedField(queryset=EspaciosFisicos.objects.all())
    periodo = serializers.PrimaryKeyRelatedField(queryset=PeriodoAcademico.objects.all())
    bloque_horario = serializers.PrimaryKeyRelatedField(queryset=BloquesHorariosDefinicion.objects.all())

    # Campos de solo lectura para obtener detalles en las respuestas GET
    grupo_detalle = GruposSerializer(source='grupo', read_only=True)
    docente_detalle = DocentesSerializer(source='docente', read_only=True)
    espacio_detalle = EspaciosFisicosSerializer(source='espacio', read_only=True)
    materia_detalle = MateriasSerializer(source='materia', read_only=True)
    bloque_horario_detalle = BloquesHorariosDefinicionSerializer(source='bloque_horario', read_only=True)
    
    class Meta:
        model = HorariosAsignados
        fields = [
            'grupo', 'materia', 'docente', 'espacio', 'periodo', 
            'dia_semana', 'bloque_horario', 'estado', 'observaciones', 'updated_at',
            # Campos de solo lectura
            'grupo_detalle', 'docente_detalle', 'espacio_detalle', 
            'materia_detalle', 'bloque_horario_detalle'
        ]
        read_only_fields = ['estado', 'updated_at'] # El estado se maneja internamente

    def create(self, validated_data):
        # El estado se puede definir por defecto aquí si es necesario
        validated_data['estado'] = 'Programado'
        return super().create(validated_data)

class ConfiguracionRestriccionesSerializer(serializers.ModelSerializer):
    periodo_aplicable_nombre = serializers.CharField(source='periodo_aplicable.nombre_periodo', read_only=True, allow_null=True)
    tipo_aplicacion_display = serializers.CharField(source='get_tipo_aplicacion_display', read_only=True)

    class Meta:
        model = ConfiguracionRestricciones
        fields = ['restriccion_id', 'codigo_restriccion', 'descripcion', 'tipo_aplicacion', 'tipo_aplicacion_display',
                  'entidad_id_1', 'entidad_id_2', 'valor_parametro',
                  'periodo_aplicable', 'periodo_aplicable_nombre', 'esta_activa']

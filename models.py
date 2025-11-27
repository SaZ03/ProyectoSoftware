import database as db
from datetime import datetime

def get_patient_history(patient_id):
    query = """
    SELECT 
        u.*,
        hm.fecha_ingreso_ux,
        hm.fecha_ingreso_piso,
        hm.tipo_interrogatorio,
        ap.enfermedades_cronicas,
        ap.alergias_antecedentes,
        ap.cirugias,
        ap.tabaquismo,
        ap.etilismo,
        anp.ocupacion,
        anp.escolaridad,
        af.condicion as antecedente_familiar,
        af.relacion
    FROM Usuario u
    LEFT JOIN HistorialMedico hm ON u.id_usuario = hm.id_paciente
    LEFT JOIN AntecedentePatologico ap ON hm.id_historial = ap.id_historial
    LEFT JOIN AntecedenteNoPatologico anp ON hm.id_historial = anp.id_historial
    LEFT JOIN AntecedenteFamiliar af ON hm.id_historial = af.id_historial
    WHERE u.id_usuario = %s
    """
    return db.execute_query(query, (patient_id,), fetch=True)

def update_patient_history(patient_id, data, medic_id):
    # 1. Verificar si existe historial médico
    check_query = "SELECT id_historial FROM HistorialMedico WHERE id_paciente = %s"
    historial = db.execute_query(check_query, (patient_id,), fetch=True)
    
    if not historial:
        # Crear historial médico si no existe
        historial_query = """
        INSERT INTO HistorialMedico (id_paciente, fecha_ingreso_ux, ultima_actualizacion)
        VALUES (%s, %s, %s)
        """
        historial_id = db.execute_query(historial_query, (patient_id, datetime.now(), datetime.now()))
    else:
        historial_id = historial[0]['id_historial']
    
    # 2. Actualizar antecedentes patológicos
    update_patologico = """
    INSERT INTO AntecedentePatologico (id_historial, enfermedades_cronicas, alergias_antecedentes, cirugias, tabaquismo, etilismo)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        enfermedades_cronicas = VALUES(enfermedades_cronicas),
        alergias_antecedentes = VALUES(alergias_antecedentes),
        cirugias = VALUES(cirugias),
        tabaquismo = VALUES(tabaquismo),
        etilismo = VALUES(etilismo)
    """
    db.execute_query(update_patologico, (
        historial_id,
        data.get('antecedentes_medicos'),
        data.get('alergias'),
        data.get('antecedentes_quirurgicos'),
        'tabaco' in data.get('habitos', ''),
        'alcohol' in data.get('habitos', '')
    ))
    
    # 3. Registrar en historial de actualizaciones
    audit_query = """
    INSERT INTO HistorialActualizacion (id_historial, id_medico, fecha, descripcion)
    VALUES (%s, %s, %s, %s)
    """
    db.execute_query(audit_query, (
        historial_id,
        medic_id,
        datetime.now(),
        f"Actualización de historial clínico"
    ))
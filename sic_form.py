import streamlit as st
from datetime import date
import pandas as pd
import re
import time
from reportlab.lib.pagesizes import letter, LEGAL
from reportlab.pdfgen import canvas
import io
from PIL import Image
from reportlab.lib.utils import ImageReader

# Configuración inicial de session_state
if 'sic_counter' not in st.session_state:
    st.session_state.sic_counter = 1
if 'solicitudes' not in st.session_state:
    st.session_state.solicitudes = {}
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Dashboard"
if 'usuarios' not in st.session_state:
    st.session_state.usuarios = {
        "admin@ccm.cl": {
            "password": "admin123",
            "rol": "Administrador",
            "nombre_completo": "Administrador del Sistema",
            "cargo": "Administrador",
            "departamento": "Informática",
            "activo": True
        },
        "creador@ccm.cl": {
            "password": "123",
            "rol": "Creador SIC",
            "nombre_completo": "Juan Pérez",
            "cargo": "Asistente Administrativo",
            "departamento": "Área Médica",
            "activo": True
        },
        "jefe.area@ccm.cl": {
            "password": "123",
            "rol": "Jefe de Área",
            "nombre_completo": "María González",
            "cargo": "Jefe Área Médica",
            "departamento": "Área Médica",
            "activo": True
        },
        "finanzas@ccm.cl": {
            "password": "123",
            "rol": "Jefe de Finanzas",
            "nombre_completo": "Carlos Rodríguez",
            "cargo": "Jefe de Finanzas",
            "departamento": "Finanzas",
            "activo": True
        },
        "supervisor@ccm.cl": {
            "password": "123",
            "rol": "Supervisor Mercado Público",
            "nombre_completo": "Ana Martínez",
            "cargo": "Supervisor de Adquisiciones",
            "departamento": "Adquisiciones",
            "activo": True
        },
        "jefe.adm@ccm.cl": {
            "password": "123",
            "rol": "Jefe Administrativo",
            "nombre_completo": "Pedro Soto",
            "cargo": "Jefe Administrativo",
            "departamento": "Administración",
            "activo": True
        },
        "director@ccm.cl": {
            "password": "123",
            "rol": "Director",
            "nombre_completo": "Luis Morales",
            "cargo": "Director CCM",
            "departamento": "Dirección",
            "activo": True
        }
    }
if 'registro_cambios' not in st.session_state:
    st.session_state.registro_cambios = []

# Mover la creación de ejemplos a una función separada
def crear_solicitudes_ejemplo():
    if 'solicitudes_ejemplo_creadas' not in st.session_state:
        st.session_state.solicitudes_ejemplo_creadas = False

    if not st.session_state.solicitudes_ejemplo_creadas and not st.session_state.solicitudes:
        # Agregar las 3 solicitudes de ejemplo solo si no hay solicitudes existentes
        st.session_state.solicitudes["SIC-2024-0001"] = {
            "num_sic": "SIC-2024-0001",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 1",
            "rut_proveedor": "11.111.111-1",
            "descripcion": "Insumos médicos",
            "motivo": "Reposición de stock",
            "valor_estimado": 1500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Finanzas (Jefe de Área ya aprobó)
        st.session_state.solicitudes["SIC-2024-0002"] = {
            "num_sic": "SIC-2024-0002",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Licitación Pública",
            "licitacion_num": "2024-01",
            "saldo": 5000000,
            "nombre_proveedor": "Proveedor 2",
            "rut_proveedor": "22.222.222-2",
            "descripcion": "Equipamiento médico",
            "motivo": "Actualización de equipos",
            "valor_estimado": 3000000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado según especificaciones", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Supervisor (Finanzas ya aprobó)
        st.session_state.solicitudes["SIC-2024-0003"] = {
            "num_sic": "SIC-2024-0003",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Compra Ágil",
            "nombre_proveedor": "Proveedor 3",
            "rut_proveedor": "33.333.333-3",
            "descripcion": "Material de oficina",
            "motivo": "Reposición mensual",
            "valor_estimado": 500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto disponible", "cdp": "CDP-2024-001", "catalogo": "CAT-001", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Jefe Administrativo
        st.session_state.solicitudes["SIC-2024-0004"] = {
            "num_sic": "SIC-2024-0004",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 4",
            "rut_proveedor": "44.444.444-4",
            "descripcion": "Equipos de computación",
            "motivo": "Renovación de equipos",
            "valor_estimado": 2500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto disponible", "cdp": "CDP-2024-002", "catalogo": "CAT-002", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Aprobado", "comentario": "Aprobado según normativa", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Solicitud pendiente de Director
        st.session_state.solicitudes["SIC-2024-0005"] = {
            "num_sic": "SIC-2024-0005",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Licitación Pública",
            "licitacion_num": "2024-02",
            "saldo": 8000000,
            "nombre_proveedor": "Proveedor 5",
            "rut_proveedor": "55.555.555-5",
            "descripcion": "Equipamiento médico especializado",
            "motivo": "Implementación nueva área",
            "valor_estimado": 7500000,
            "estado": "Pendiente",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "jefe_area": {"estado": "Aprobado", "comentario": "Aprobado", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "finanzas": {"estado": "Aprobado", "comentario": "Presupuesto aprobado", "cdp": "CDP-2024-003", "catalogo": "CAT-003", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "supervisor": {"estado": "Aprobado", "comentario": "Proceso licitatorio correcto", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "jefe_adm": {"estado": "Aprobado", "comentario": "Aprobado según procedimientos", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
            }
        }

        # Agregar esta SIC en la función crear_solicitudes_ejemplo()
        # Solicitud completamente aprobada
        st.session_state.solicitudes["SIC-2024-0006"] = {
            "num_sic": "SIC-2024-0006",
            "fecha": date.today(),
            "area_origen": "Área Médica",
            "destinatario": "Director del CCM 'Coyhaique'",
            "tipo_compra": "Convenio Marco",
            "nombre_proveedor": "Proveedor 6",
            "rut_proveedor": "66.666.666-6",
            "descripcion": "Equipamiento de laboratorio",
            "motivo": "Actualización de equipos de laboratorio clínico",
            "valor_estimado": 4500000,
            "estado": "Aprobado",
            "creador": {
                "nombre": "Juan Pérez",
                "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
            },
            "aprobaciones": {
                "finanzas": {
                    "estado": "Aprobado", 
                    "comentario": "Presupuesto disponible", 
                    "cdp": "CDP-2024-004",
                    "catalogos": [  # Cambiar de "catalogo" a "catalogos" como lista
                        {
                            "numero": "22-01-001",
                            "monto": 2500000
                        },
                        {
                            "numero": "22-02-001",
                            "monto": 2000000
                        }
                    ],
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "jefe_area": {
                    "estado": "Aprobado", 
                    "comentario": "Equipamiento necesario para el servicio", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "supervisor": {
                    "estado": "Aprobado", 
                    "comentario": "Proceso de compra validado", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "jefe_adm": {
                    "estado": "Aprobado", 
                    "comentario": "Documentación completa", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                },
                "director": {
                    "estado": "Aprobado", 
                    "comentario": "Se autoriza la compra", 
                    "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}
                }
            }
        }

        st.session_state.solicitudes_ejemplo_creadas = True
        st.session_state.sic_counter = 7  # Actualizado para empezar después de los ejemplos

def login():
    st.sidebar.header("Inicio de Sesión")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if st.sidebar.button("Iniciar Sesión"):
        if email in st.session_state.usuarios:
            user_data = st.session_state.usuarios[email]
            if user_data["password"] == password:
                if user_data["activo"]:
                    st.session_state.user = email
                    st.session_state.rol = user_data["rol"]
                    return True
                else:
                    st.sidebar.error("Usuario desactivado")
            else:
                st.sidebar.error("Contraseña incorrecta")
        else:
            st.sidebar.error("Email no encontrado")
    return False

def crear_sic():
    st.title("Crear Nueva Solicitud Interna de Compra (SIC)")
    
    # Control de pasos en session_state
    if 'paso_creacion' not in st.session_state:
        st.session_state.paso_creacion = 1
    
    # Generar número SIC
    año_actual = date.today().year
    num_sic = f"SIC-{año_actual}-{st.session_state.sic_counter:04d}"
    
    # PASO 1: Información básica y tipo de compra
    if st.session_state.paso_creacion == 1:
        with st.form("paso1_form"):
            st.write(f"N° SIC: {num_sic}")
            fecha = st.date_input("Fecha", value=date.today())
            
            # Modificar el campo de área para usar un selectbox con opciones limitadas
            area_origen = st.selectbox(
                "Área",
                [
                    "Área Médica",
                    "Área Administrativa",
                    "Enfermerías"
                ]
            )
            
            destinatario = st.text_input("Destinatario", value="Director del CCM 'Coyhaique'")
            
            # Declaración de conflicto de interés
            st.subheader("Declaración de Conflicto de Interés")
            conflicto_creador = st.radio(
                "¿Tiene algún conflicto de interés con esta compra?",
                ["No", "Sí"],
                horizontal=True,
                key="conflicto_creador",
                index=None
            )
            
            if conflicto_creador == "Sí":
                detalle_conflicto = st.text_area(
                    "Por favor, detalle el conflicto de interés:",
                    key="detalle_conflicto_creador"
                )
            else:
                detalle_conflicto = ""
            
            # Selección de tipo de compra
            tipo_compra = st.radio(
                "Tipo de Compra",
                ["Convenio Marco", "Licitación Pública", "Compra Ágil"],
                horizontal=True,
                key="tipo_compra",
                index=None
            )
            
            submitted = st.form_submit_button("Siguiente")
            
            if submitted:
                if not tipo_compra:
                    st.error("Debe seleccionar un tipo de compra")
                    return
                if not conflicto_creador:
                    st.error("Debe declarar si existe o no conflicto de interés")
                    return
                if conflicto_creador == "Sí" and not detalle_conflicto:
                    st.error("Debe detallar el conflicto de interés")
                    return
                
                # Guardar datos del paso 1 en session_state
                st.session_state.paso1_datos = {
                    "num_sic": num_sic,
                    "fecha": fecha,
                    "area_origen": area_origen,
                    "destinatario": destinatario,
                    "conflicto_creador": conflicto_creador,
                    "detalle_conflicto": detalle_conflicto,
                    "tipo_compra": tipo_compra
                }
                
                # Avanzar al siguiente paso
                st.session_state.paso_creacion = 2
                st.rerun()

    # PASO 2: Campos específicos según tipo de compra
    elif st.session_state.paso_creacion == 2:
        st.subheader("Detalles de la Compra")
        datos_paso1 = st.session_state.paso1_datos
        
        # Mostrar resumen del paso 1
        with st.expander("Resumen del Paso 1", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Información Básica")
                st.write(f"N° SIC: {datos_paso1['num_sic']}")
                st.write(f"Fecha: {datos_paso1['fecha']}")
                st.write(f"Área: {datos_paso1['area_origen']}")
                st.write(f"Destinatario: {datos_paso1['destinatario']}")
            with col2:
                st.write("### Tipo de Compra")
                st.write(f"Tipo seleccionado: {datos_paso1['tipo_compra']}")
                st.write("### Conflicto de Interés")
                st.write(f"Declaración: {datos_paso1['conflicto_creador']}")
                if datos_paso1['conflicto_creador'] == "Sí":
                    st.write(f"Detalle: {datos_paso1['detalle_conflicto']}")
        
        st.markdown("---")
        
        # Formulario del paso 2
        with st.form("paso2_form"):
            # Campos específicos para Licitación Pública
            if datos_paso1["tipo_compra"] == "Licitación Pública":
                col1, col2 = st.columns(2)
                with col1:
                    licitacion_num = st.text_input("ID Licitación")
                    nombre_proveedor = st.text_input("Nombre del Proveedor")
                with col2:
                    saldo = st.number_input(
                        "Saldo Disponible ($)",
                        min_value=0,
                        step=1000,
                        help="Saldo disponible para la licitación"
                    )
                    rut_proveedor = st.text_input(
                        "RUT del Proveedor",
                        placeholder="XX.XXX.XXX-X"
                    )
            else:
                licitacion_num = None
                saldo = None
                nombre_proveedor = None
                rut_proveedor = None
            
            # Campos comunes para todos los tipos
            descripcion_compra = st.text_area("Se solicita la compra de")
            motivo_solicitud = st.text_area("Motivo y fundamento de la solicitud")
            valor_estimado = st.number_input(
                "Valor Estimado de la Compra ($)",
                min_value=0,
                value=None,
                step=1000,
                placeholder="Ingrese el valor estimado"
            )
            
            # Subida de archivos
            st.subheader("Documentos de Respaldo")
            archivos_subidos = st.file_uploader(
                "Subir documentos de respaldo",
                accept_multiple_files=True,
                type=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'],
                help="Formatos permitidos: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Crear Solicitud")
            with col2:
                if st.form_submit_button("Volver"):
                    st.session_state.paso_creacion = 1
                    st.rerun()

            if submitted:
                # Validaciones según tipo de compra
                if datos_paso1["tipo_compra"] == "Licitación Pública":
                    if not all([licitacion_num, saldo, nombre_proveedor, rut_proveedor]):
                        st.error("Para Licitación Pública, todos los campos son obligatorios")
                        return
                
                # Validaciones comunes
                if not descripcion_compra:
                    st.error("La descripción de la compra es obligatoria")
                    return
                if not motivo_solicitud:
                    st.error("El motivo de la solicitud es obligatorio")
                    return
                if not valor_estimado:
                    st.error("El valor estimado es obligatorio")
                    return
                
                # Procesar archivos subidos
                archivos_guardados = []
                if archivos_subidos:
                    for archivo in archivos_subidos:
                        archivo_info = {
                            "nombre": archivo.name,
                            "tipo": archivo.type,
                            "contenido": archivo.getvalue()
                        }
                        archivos_guardados.append(archivo_info)
                
                # Crear nueva solicitud
                nueva_solicitud = {
                    **datos_paso1,  # Incluir datos del paso 1
                    "descripcion": descripcion_compra,
                    "motivo": motivo_solicitud,
                    "valor_estimado": valor_estimado,
                    "licitacion_num": licitacion_num if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "saldo": saldo if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "nombre_proveedor": nombre_proveedor if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "rut_proveedor": rut_proveedor if datos_paso1["tipo_compra"] == "Licitación Pública" else None,
                    "archivos": archivos_guardados,
                    "estado": "Pendiente",
                    "creador": {
                        "nombre": st.session_state.usuarios[st.session_state.user]['nombre_completo'],
                        "conflicto_interes": {
                            "tiene_conflicto": datos_paso1["conflicto_creador"],
                            "detalle": datos_paso1.get("detalle_conflicto", "")
                        }
                    },
                    "aprobaciones": {
                        "jefe_area": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "finanzas": {"estado": "Pendiente", "comentario": "", "cdp": "", "catalogo": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "supervisor": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "jefe_adm": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}},
                        "director": {"estado": "Pendiente", "comentario": "", "conflicto_interes": {"tiene_conflicto": "No", "detalle": ""}}
                    }
                }  # Cierre del diccionario nueva_solicitud
                
                # Guardar solicitud y limpiar estado
                st.session_state.solicitudes[datos_paso1["num_sic"]] = nueva_solicitud
                st.session_state.sic_counter += 1
                del st.session_state.paso_creacion
                del st.session_state.paso1_datos
                
                st.success(f"Solicitud {datos_paso1['num_sic']} creada exitosamente")
                st.session_state.current_tab = "Dashboard"
                time.sleep(1)
                st.rerun()

def revisar_solicitudes():
    st.title("Revisar Solicitudes")
    
    if not st.session_state.solicitudes:
        st.warning("No hay solicitudes pendientes")
        return

    # Filtrar solicitudes según el rol y estado
    solicitudes_pendientes = {}
    for num_sic, solicitud in st.session_state.solicitudes.items():
        if st.session_state.rol == "Jefe de Área":
            # Solo mostrar solicitudes del área médica
            if solicitud['area_origen'] == "Área Médica" and solicitud['aprobaciones']['jefe_area']['estado'] == "Pendiente":
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Jefe de Finanzas":
            # Mostrar solicitudes que:
            # 1. No son del área médica (pasan directo)
            # 2. Son del área médica y ya fueron aprobadas por el jefe de área
            if (solicitud['area_origen'] != "Área Médica" and solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente") or \
               (solicitud['area_origen'] == "Área Médica" and solicitud['aprobaciones']['jefe_area']['estado'] == "Aprobado" and \
                solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Supervisor Mercado Público":
            if (solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['supervisor']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Jefe Administrativo":
            if (solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['jefe_adm']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud
        
        elif st.session_state.rol == "Director":
            if (solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado" and 
                solicitud['aprobaciones']['director']['estado'] == "Pendiente"):
                solicitudes_pendientes[num_sic] = solicitud

    if not solicitudes_pendientes:
        st.info(f"No hay solicitudes pendientes para {st.session_state.rol}")
        return

    # Mostrar solo las solicitudes pendientes filtradas
    for num_sic, solicitud in solicitudes_pendientes.items():
        with st.expander(f"Solicitud {num_sic} - Pendiente de aprobación"):
            # Mostrar detalles básicos de la solicitud
            st.write(f"Fecha: {solicitud['fecha']}")
            st.write(f"Área: {solicitud['area_origen']}")
            st.write(f"Proveedor: {solicitud['nombre_proveedor']}")
            
            # Manejar el valor estimado de forma segura
            valor_estimado = solicitud['valor_estimado']
            if valor_estimado is not None:
                st.write(f"Valor Estimado: ${valor_estimado:,}")
            else:
                st.write("Valor Estimado: No especificado")
            
            st.write(f"Descripción: {solicitud['descripcion']}")
            st.write(f"Tipo de Compra: {solicitud['tipo_compra']}")
            
            # Manejar los campos de licitación de forma segura
            if solicitud['tipo_compra'] == "Licitación Pública":
                st.write(f"N° Licitación: {solicitud['licitacion_num'] or 'No especificado'}")
                saldo = solicitud['saldo']
                if saldo is not None:
                    st.write(f"Saldo Disponible: ${saldo:,}")
                else:
                    st.write("Saldo Disponible: No especificado")
            
            # Mostrar declaraciones de conflicto según el rol
            st.subheader("Declaraciones de Conflicto de Interés")
            
            # Siempre mostrar la declaración del creador
            st.write(f"Creador: {solicitud['creador']['conflicto_interes']['tiene_conflicto']}")
            
            if st.session_state.rol == "Jefe de Finanzas":
                # Mostrar solo declaración del creador y jefe de área
                if solicitud['aprobaciones']['jefe_area']['estado'] != "Pendiente":
                    st.write(f"Jefe de Área: {solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto']}")
            
            elif st.session_state.rol == "Supervisor Mercado Público":
                # Mostrar declaraciones hasta finanzas
                if solicitud['aprobaciones']['jefe_area']['estado'] != "Pendiente":
                    st.write(f"Jefe de Área: {solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto']}")
                if solicitud['aprobaciones']['finanzas']['estado'] != "Pendiente":
                    st.write(f"Finanzas: {solicitud['aprobaciones']['finanzas']['conflicto_interes']['tiene_conflicto']}")
            
            elif st.session_state.rol == "Jefe Administrativo" and solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['jefe_adm']['estado'] == "Pendiente":
                    conflicto = st.radio(
                        "¿Tiene algún conflicto de interés con esta compra?",
                        ["No", "Sí"],
                        key=f"conflicto_jefe_adm_{num_sic}",
                        horizontal=True,
                        index=None
                    )
                    
                    detalle_conflicto = ""
                    if conflicto == "Sí":
                        detalle_conflicto = st.text_area(
                            "Por favor, detalle el conflicto de interés:",
                            key=f"detalle_conflicto_jefe_adm_{num_sic}"
                        )
                    
                    estado = st.radio(
                        "Estado de aprobación",
                        ["Aprobado", "Rechazado"],
                        key=f"radio_jefe_adm_{num_sic}",
                        index=None
                    )
                    comentario = st.text_area(
                        "Comentario",
                        key=f"comentario_jefe_adm_{num_sic}"
                    )
                    if st.button("Guardar decisión", key=f"btn_jefe_adm_{num_sic}"):
                        if conflicto is None or estado is None:
                            st.error("Por favor, complete todos los campos antes de guardar")
                        else:
                            solicitud['aprobaciones']['jefe_adm']['estado'] = estado
                            solicitud['aprobaciones']['jefe_adm']['comentario'] = comentario
                            solicitud['aprobaciones']['jefe_adm']['conflicto_interes'] = {
                                "tiene_conflicto": conflicto,
                                "detalle": detalle_conflicto
                            }
                            st.success("Decisión guardada")
                            st.rerun()
            
            elif st.session_state.rol == "Director" and solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['director']['estado'] == "Pendiente":
                    conflicto = st.radio(
                        "¿Tiene algún conflicto de interés con esta compra?",
                        ["No", "Sí"],
                        key=f"conflicto_director_{num_sic}",
                        horizontal=True,
                        index=None
                    )
                    
                    detalle_conflicto = ""
                    if conflicto == "Sí":
                        detalle_conflicto = st.text_area(
                            "Por favor, detalle el conflicto de interés:",
                            key=f"detalle_conflicto_director_{num_sic}"
                        )
                    
                    estado = st.radio(
                        "Estado de aprobación",
                        ["Aprobado", "Rechazado"],
                        key=f"radio_director_{num_sic}",
                        index=None
                    )
                    comentario = st.text_area(
                        "Comentario",
                        key=f"comentario_director_{num_sic}"
                    )
                    if st.button("Guardar decisión", key=f"btn_director_{num_sic}"):
                        if conflicto is None or estado is None:
                            st.error("Por favor, complete todos los campos antes de guardar")
                        else:
                            solicitud['aprobaciones']['director']['estado'] = estado
                            solicitud['aprobaciones']['director']['comentario'] = comentario
                            solicitud['aprobaciones']['director']['conflicto_interes'] = {
                                "tiene_conflicto": conflicto,
                                "detalle": detalle_conflicto
                            }
                            st.success("Decisión guardada")
                            st.rerun()
            
            # Sección de aprobación según rol
            if st.session_state.rol == "Jefe de Área":
                if solicitud['aprobaciones']['jefe_area']['estado'] == "Pendiente":
                    conflicto = st.radio(
                        "¿Tiene algún conflicto de interés con esta compra?",
                        ["No", "Sí"],
                        key=f"conflicto_jefe_area_{num_sic}",
                        horizontal=True,
                        index=None
                    )
                    
                    detalle_conflicto = ""
                    if conflicto == "Sí":
                        detalle_conflicto = st.text_area(
                            "Por favor, detalle el conflicto de interés:",
                            key=f"detalle_conflicto_jefe_area_{num_sic}"
                        )
                    
                    estado = st.radio(
                        "Estado de aprobación",
                        ["Aprobado", "Rechazado"],
                        key=f"radio_jefe_area_{num_sic}",
                        index=None
                    )
                    comentario = st.text_area(
                        "Comentario",
                        key=f"comentario_jefe_area_{num_sic}"
                    )
                    if st.button("Guardar decisión", key=f"btn_jefe_area_{num_sic}"):
                        if conflicto is None or estado is None:
                            st.error("Por favor, complete todos los campos antes de guardar")
                        else:
                            solicitud['aprobaciones']['jefe_area']['estado'] = estado
                            solicitud['aprobaciones']['jefe_area']['comentario'] = comentario
                            solicitud['aprobaciones']['jefe_area']['conflicto_interes'] = {
                                "tiene_conflicto": conflicto,
                                "detalle": detalle_conflicto
                            }
                            st.success("Decisión guardada")
                            st.rerun()
            
            elif st.session_state.rol == "Jefe de Finanzas" and solicitud['aprobaciones']['jefe_area']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente":
                    conflicto = st.radio(
                        "¿Tiene algún conflicto de inters con esta compra?",
                        ["No", "Sí"],
                        key=f"conflicto_finanzas_{num_sic}",
                        horizontal=True,
                        index=None
                    )
                    
                    detalle_conflicto = ""
                    if conflicto == "Sí":
                        detalle_conflicto = st.text_area(
                            "Por favor, detalle el conflicto de interés:",
                            key=f"detalle_conflicto_finanzas_{num_sic}"
                        )
                    
                    # Sección de Catálogos
                    st.subheader("Catálogos")
                    st.write(f"Valor total de la SIC: ${solicitud['valor_estimado']:,}")
                    
                    # Inicializar lista de catálogos en session_state si no existe
                    if f"catalogos_{num_sic}" not in st.session_state:
                        st.session_state[f"catalogos_{num_sic}"] = [{"numero": "", "monto": 0}]
                    
                    # Mostrar catálogos existentes
                    suma_catalogos = 0
                    catalogos_a_eliminar = []
                    
                    for i, catalogo in enumerate(st.session_state[f"catalogos_{num_sic}"]):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            catalogo["numero"] = st.text_input(
                                "Número de Catálogo",
                                value=catalogo["numero"],
                                key=f"cat_num_{num_sic}_{i}"
                            )
                        with col2:
                            catalogo["monto"] = st.number_input(
                                "Monto ($)",
                                value=catalogo["monto"],
                                min_value=0,
                                step=1000,
                                key=f"cat_monto_{num_sic}_{i}"
                            )
                        with col3:
                            if st.button("Eliminar", key=f"del_cat_{num_sic}_{i}"):
                                catalogos_a_eliminar.append(i)
                        
                        suma_catalogos += catalogo["monto"]
                    
                    # Eliminar catálogos marcados
                    for i in reversed(catalogos_a_eliminar):
                        st.session_state[f"catalogos_{num_sic}"].pop(i)
                    
                    # Botón para agregar nuevo catálogo
                    if st.button("Agregar Catálogo", key=f"add_cat_{num_sic}"):
                        st.session_state[f"catalogos_{num_sic}"].append({"numero": "", "monto": 0})
                        st.rerun()
                    
                    # Mostrar suma total y diferencia
                    st.write(f"Suma total de catálogos: ${suma_catalogos:,}")
                    diferencia = solicitud['valor_estimado'] - suma_catalogos
                    if diferencia != 0:
                        st.warning(f"La suma de catálogos {'excede' if diferencia < 0 else 'no alcanza'} el valor de la SIC por ${abs(diferencia):,}")
                    else:
                        st.success("La suma de catálogos coincide con el valor de la SIC")
                    
                    # CDP y estado de aprobación
                    cdp = st.text_input("Número CDP", key=f"cdp_finanzas_{num_sic}")
                    estado = st.radio(
                        "Estado de aprobación",
                        ["Aprobado", "Rechazado"],
                        key=f"radio_finanzas_{num_sic}",
                        index=None
                    )
                    comentario = st.text_area(
                        "Comentario",
                        key=f"comentario_finanzas_{num_sic}"
                    )
                    
                    # Botón de previsualización del CDP
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Previsualizar CDP", key=f"preview_cdp_{num_sic}"):
                            # Crear una copia temporal de la solicitud con los datos actuales
                            solicitud_temp = solicitud.copy()
                            solicitud_temp['aprobaciones']['finanzas']['cdp'] = cdp
                            solicitud_temp['aprobaciones']['finanzas']['catalogos'] = st.session_state[f"catalogos_{num_sic}"]
                            
                            st.write("### Previsualización del CDP")
                            cdp_buffer = generar_cdp(solicitud_temp)
                            st.download_button(
                                label="Descargar Previsualización",
                                data=cdp_buffer,
                                file_name=f"CDP_{solicitud['num_sic']}_preview.pdf",
                                mime="application/pdf",
                                key=f"cdp_preview_download_{num_sic}"
                            )
                    
                    with col2:
                        if st.button("Guardar decisión", key=f"btn_finanzas_{num_sic}"):
                            if conflicto is None or estado is None:
                                st.error("Por favor, complete todos los campos antes de guardar")
                            elif diferencia != 0:
                                st.error("La suma de catálogos debe ser igual al valor de la SIC")
                            else:
                                solicitud['aprobaciones']['finanzas']['estado'] = estado
                                solicitud['aprobaciones']['finanzas']['comentario'] = comentario
                                solicitud['aprobaciones']['finanzas']['cdp'] = cdp
                                solicitud['aprobaciones']['finanzas']['catalogos'] = st.session_state[f"catalogos_{num_sic}"]
                                solicitud['aprobaciones']['finanzas']['conflicto_interes'] = {
                                    "tiene_conflicto": conflicto,
                                    "detalle": detalle_conflicto
                                }
                                st.success("Decisión guardada")
                                
                                # Generar CDP solo si la decisión es "Aprobado"
                                if estado == "Aprobado":
                                    st.write("### Certificado de Disponibilidad Presupuestaria")
                                    cdp_buffer = generar_cdp(solicitud)
                                    st.download_button(
                                        label="Descargar Certificado de Disponibilidad Presupuestaria",
                                        data=cdp_buffer,
                                        file_name=f"CDP_{solicitud['num_sic']}.pdf",
                                        mime="application/pdf",
                                        key=f"cdp_download_{num_sic}"
                                    )
                                
                                st.rerun()

            elif st.session_state.rol == "Supervisor Mercado Público" and solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['supervisor']['estado'] == "Pendiente":
                    conflicto = st.radio(
                        "¿Tiene algún conflicto de interés con esta compra?",
                        ["No", "Sí"],
                        key=f"conflicto_supervisor_{num_sic}",
                        horizontal=True,
                        index=None
                    )
                    
                    detalle_conflicto = ""
                    if conflicto == "Sí":
                        detalle_conflicto = st.text_area(
                            "Por favor, detalle el conflicto de interés:",
                            key=f"detalle_conflicto_supervisor_{num_sic}"
                        )
                    
                    estado = st.radio(
                        "Estado de aprobación",
                        ["Aprobado", "Rechazado"],
                        key=f"radio_supervisor_{num_sic}",
                        index=None
                    )
                    comentario = st.text_area(
                        "Comentario",
                        key=f"comentario_supervisor_{num_sic}"
                    )
                    if st.button("Guardar decisión", key=f"btn_supervisor_{num_sic}"):
                        if conflicto is None or estado is None:
                            st.error("Por favor, complete todos los campos antes de guardar")
                        else:
                            solicitud['aprobaciones']['supervisor']['estado'] = estado
                            solicitud['aprobaciones']['supervisor']['comentario'] = comentario
                            solicitud['aprobaciones']['supervisor']['conflicto_interes'] = {
                                "tiene_conflicto": conflicto,
                                "detalle": detalle_conflicto
                            }
                            st.success("Decisión guardada")
                            st.rerun()

            # Mostrar archivos adjuntos si existen
            if 'archivos' in solicitud and solicitud['archivos']:
                st.subheader("Documentos Adjuntos")
                for i, archivo in enumerate(solicitud['archivos']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📎 {archivo['nombre']} ({archivo['tipo']})")
                    with col2:
                        st.download_button(
                            label="Descargar",
                            data=archivo['contenido'],
                            file_name=archivo['nombre'],
                            mime=archivo['tipo'],
                            key=f"download_{num_sic}_{i}"
                        )
                
                st.markdown("---")  # Separador después de los documentos
            
            # Mostrar CDP solo si está aprobado por Finanzas
            if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                st.write("### Certificado de Disponibilidad Presupuestaria")
                cdp_buffer = generar_cdp(solicitud)
                st.download_button(
                    label="Descargar CDP",
                    data=cdp_buffer,
                    file_name=f"CDP_{solicitud['num_sic']}.pdf",
                    mime="application/pdf",
                    key=f"cdp_download_{num_sic}"
                )
            
            # Mostrar Resumen SIC solo si está aprobado por el Director
            if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                st.write("### Resumen SIC")
                st.download_button(
                    label="Descargar Resumen SIC",
                    data=generar_resumen_sic(solicitud),
                    file_name=f"SIC_{solicitud['num_sic']}_Resumen.pdf",
                    mime="application/pdf",
                    key=f"download_resumen_{num_sic}"
                )

def mostrar_resumen_solicitudes():
    st.header("Resumen de Solicitudes")
    
    if not st.session_state.solicitudes:
        st.info("No hay solicitudes registradas")
        return

    # Crear DataFrame para mejor visualización
    import pandas as pd
    
    datos_resumen = []
    for num_sic, solicitud in st.session_state.solicitudes.items():
        # Determinar estado general
        estado_actual = "Pendiente"
        if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
            estado_actual = "Aprobado"
        elif any(apr['estado'] == "Rechazado" for apr in solicitud['aprobaciones'].values()):
            estado_actual = "Rechazado"
        
        # Formatear el valor estimado de manera segura
        valor_estimado = solicitud['valor_estimado']
        valor_formateado = f"${valor_estimado:,}" if valor_estimado is not None else "No especificado"
        
        # Crear fila de datos
        fila = {
            'N° SIC': num_sic,
            'Fecha': solicitud['fecha'],
            'Área': solicitud['area_origen'],
            'Proveedor': solicitud['nombre_proveedor'],
            'Valor ($)': valor_formateado,
            'Estado': estado_actual,
            'Jefe Área': "N/A" if solicitud['area_origen'] in ["Área Administrativa", "Enfermerías"] else solicitud['aprobaciones']['jefe_area']['estado'],
            'N° CDP': solicitud['aprobaciones']['finanzas']['cdp'] or 'Pendiente',
            'Finanzas': solicitud['aprobaciones']['finanzas']['estado'],
            'Supervisor': solicitud['aprobaciones']['supervisor']['estado'],
            'Jefe Adm': solicitud['aprobaciones']['jefe_adm']['estado'],
            'Director': solicitud['aprobaciones']['director']['estado']
        }
        datos_resumen.append(fila)
    
    df = pd.DataFrame(datos_resumen)
    
    # Agregar columna de acción para ver detalles
    df['Acciones'] = 'Ver Detalles'

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        estado_filtro = st.multiselect(
            "Filtrar por Estado",
            options=["Pendiente", "Aprobado", "Rechazado"],
            default=["Pendiente", "Aprobado", "Rechazado"]
        )
    with col2:
        fecha_filtro = st.date_input(
            "Filtrar desde fecha",
            value=None
        )
    
    # Aplicar filtros
    if fecha_filtro:
        df = df[df['Fecha'] >= fecha_filtro]
    if estado_filtro:
        df = df[df['Estado'].isin(estado_filtro)]

    # Estilo del DataFrame
    def highlight_estado(val):
        if val == "Aprobado":
            return 'background-color: #90EE90'
        elif val == "Rechazado":
            return 'background-color: #FFB6C1'
        return ''

    # Mostrar DataFrame con estilo
    st.dataframe(
        df.style.applymap(highlight_estado, subset=['Estado', 'Jefe Área', 'Finanzas', 'Supervisor', 'Jefe Adm', 'Director']),
        use_container_width=True
    )

    # Selector para ver detalles
    num_sic_seleccionado = st.selectbox(
        "Seleccionar SIC para ver detalles",
        options=df['N° SIC'].tolist(),
        format_func=lambda x: f"Ver detalles de {x}"
    )

    if num_sic_seleccionado:
        solicitud = st.session_state.solicitudes[num_sic_seleccionado]
        
        # Mostrar detalles completos en un expander
        with st.expander(f"Detalles completos de {num_sic_seleccionado}", expanded=True):
            # Información del Creador
            st.write("### Información del Creador")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**SOLICITANTE:**")
                st.write(solicitud['creador']['nombre'])
            with col2:
                st.write("**ÁREA:**")
                st.write(solicitud['area_origen'])
            with col3:
                st.write("**TIPO DE COMPRA:**")
                st.write(solicitud['tipo_compra'])
            
            if solicitud['tipo_compra'] == "Licitación Pública":
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**N° LICITACIÓN:**")
                    st.write(solicitud['licitacion_num'])
                with col2:
                    st.write("**SALDO:**")
                    st.write(f"${solicitud['saldo']:,.0f}".replace(",", "."))
                with col3:
                    st.write("**VALOR ESTIMADO:**")
                    st.write(f"${solicitud['valor_estimado']:,.0f}".replace(",", "."))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**PROVEEDOR:**")
                    st.write(solicitud['nombre_proveedor'])
                with col2:
                    st.write("**RUT:**")
                    st.write(solicitud['rut_proveedor'])
            else:
                st.write("**VALOR ESTIMADO:**")
                st.write(f"${solicitud['valor_estimado']:,.0f}".replace(",", "."))
            
            st.write("**CONFLICTO:**")
            st.write(solicitud['creador']['conflicto_interes']['tiene_conflicto'])
            if solicitud['creador']['conflicto_interes']['tiene_conflicto'] == "Sí":
                st.write("**DETALLE CONFLICTO:**")
                st.write(solicitud['creador']['conflicto_interes']['detalle'])
            
            st.write("**DESCRIPCIÓN:**")
            st.write(solicitud['descripcion'])
            
            st.write("**MOTIVO:**")
            st.write(solicitud['motivo'])
            
            st.markdown("---")  # Separador
            
            # Información de Aprobaciones
            if solicitud['aprobaciones']['jefe_area']['estado'] != "Pendiente":
                st.write("### Aprobación Jefe de Área")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**ESTADO:**")
                    st.write(solicitud['aprobaciones']['jefe_area']['estado'])
                with col2:
                    st.write("**FECHA:**")
                    st.write(solicitud['fecha'].strftime('%d-%m-%Y'))
                with col3:
                    st.write("**CONFLICTO:**")
                    st.write(solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto'])
                
                if solicitud['aprobaciones']['jefe_area']['comentario']:
                    st.write("**COMENTARIO:**")
                    st.write(solicitud['aprobaciones']['jefe_area']['comentario'])
                
                st.markdown("---")
            
            # Información de Finanzas si está aprobado
            if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                st.write("### Aprobación Jefe de Finanzas")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**ESTADO:**")
                    st.write(solicitud['aprobaciones']['finanzas']['estado'])
                with col2:
                    st.write("**FECHA:**")
                    st.write(solicitud['fecha'].strftime('%d-%m-%Y'))
                with col3:
                    st.write("**CONFLICTO:**")
                    st.write(solicitud['aprobaciones']['finanzas']['conflicto_interes']['tiene_conflicto'])
                
                st.write("**N° CDP:**")
                st.write(solicitud['aprobaciones']['finanzas']['cdp'])
                
                if 'catalogos' in solicitud['aprobaciones']['finanzas']:
                    st.write("**DISTRIBUCIÓN PRESUPUESTARIA:**")
                    for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
                        if catalogo['numero'] and catalogo['monto'] > 0:
                            st.write(f"{catalogo['numero']}: ${catalogo['monto']:,.0f}".replace(",", "."))
                
                if solicitud['aprobaciones']['finanzas']['comentario']:
                    st.write("**COMENTARIO:**")
                    st.write(solicitud['aprobaciones']['finanzas']['comentario'])
                
                st.markdown("---")

            # Información del Supervisor si está aprobado
            if solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado":
                st.write("### Aprobación Supervisor Mercado Público")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**ESTADO:**")
                    st.write(solicitud['aprobaciones']['supervisor']['estado'])
                with col2:
                    st.write("**FECHA:**")
                    st.write(solicitud['fecha'].strftime('%d-%m-%Y'))
                with col3:
                    st.write("**CONFLICTO:**")
                    st.write(solicitud['aprobaciones']['supervisor']['conflicto_interes']['tiene_conflicto'])
                
                if solicitud['aprobaciones']['supervisor']['comentario']:
                    st.write("**COMENTARIO:**")
                    st.write(solicitud['aprobaciones']['supervisor']['comentario'])
                
                st.markdown("---")
            
            # Información del Jefe Administrativo si está aprobado
            if solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado":
                st.write("### Aprobación Jefe Administrativo")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**ESTADO:**")
                    st.write(solicitud['aprobaciones']['jefe_adm']['estado'])
                with col2:
                    st.write("**FECHA:**")
                    st.write(solicitud['fecha'].strftime('%d-%m-%Y'))
                with col3:
                    st.write("**CONFLICTO:**")
                    st.write(solicitud['aprobaciones']['jefe_adm']['conflicto_interes']['tiene_conflicto'])
                
                if solicitud['aprobaciones']['jefe_adm']['comentario']:
                    st.write("**COMENTARIO:**")
                    st.write(solicitud['aprobaciones']['jefe_adm']['comentario'])
                
                st.markdown("---")
            
            # Información del Director si está aprobado
            if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                st.write("### Aprobación Director")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write("**ESTADO:**")
                    st.write(solicitud['aprobaciones']['director']['estado'])
                with col2:
                    st.write("**FECHA:**")
                    st.write(solicitud['fecha'].strftime('%d-%m-%Y'))
                with col3:
                    st.write("**CONFLICTO:**")
                    st.write(solicitud['aprobaciones']['director']['conflicto_interes']['tiene_conflicto'])
                
                if solicitud['aprobaciones']['director']['comentario']:
                    st.write("**COMENTARIO:**")
                    st.write(solicitud['aprobaciones']['director']['comentario'])
                
                st.markdown("---")

            # Sección de documentos al final
            st.write("### Documentos")
            col1, col2 = st.columns(2)
            
            # CDP si existe
            with col1:
                if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                    st.download_button(
                        label="Ver CDP",
                        data=generar_cdp(solicitud),
                        file_name=f"CDP_{solicitud['num_sic']}.pdf",
                        mime="application/pdf",
                        key=f"ver_cdp_{num_sic_seleccionado}"
                    )
            
            # Resumen SIC si está aprobada por el Director
            with col2:
                if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                    st.download_button(
                        label="Ver Resumen SIC con Firmas",
                        data=generar_resumen_sic(solicitud),
                        file_name=f"SIC_{solicitud['num_sic']}_Resumen.pdf",
                        mime="application/pdf",
                        key=f"ver_resumen_{num_sic_seleccionado}"
                    )

            # Mostrar documentos adjuntos si existen
            st.write("### Documentos Adjuntos")
            if 'archivos' in solicitud and solicitud['archivos']:
                for i, archivo in enumerate(solicitud['archivos']):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"📎 {archivo['nombre']} ({archivo['tipo']})")
                    with col2:
                        st.download_button(
                            label="Descargar",
                            data=archivo['contenido'],
                            file_name=archivo['nombre'],
                            mime=archivo['tipo'],
                            key=f"download_detalle_{num_sic_seleccionado}_{i}"
                        )
            else:
                st.info("No hay documentos adjuntos")
            
            st.markdown("---")  # Separador
            
            # Sección de documentos del sistema
            st.write("### Documentos del Sistema")
            col1, col2 = st.columns(2)
            
            # CDP si existe
            with col1:
                if solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
                    st.download_button(
                        label="Ver CDP",
                        data=generar_cdp(solicitud),
                        file_name=f"CDP_{solicitud['num_sic']}.pdf",
                        mime="application/pdf",
                        key=f"ver_cdp_detalle_{num_sic_seleccionado}"
                    )
            
            # Resumen SIC si está aprobada por el Director
            with col2:
                if solicitud['aprobaciones']['director']['estado'] == "Aprobado":
                    st.download_button(
                        label="Ver Resumen SIC con Firmas",
                        data=generar_resumen_sic(solicitud),
                        file_name=f"SIC_{solicitud['num_sic']}_Resumen.pdf",
                        mime="application/pdf",
                        key=f"ver_resumen_detalle_{num_sic_seleccionado}"
                    )

def mostrar_dashboard_aprobaciones():
    st.header("Panel de Control de Aprobaciones")
    
    # Estadísticas al inicio del dashboard
    st.subheader("Estadísticas Generales")
    
    # Crear DataFrame para las estadísticas
    df = pd.DataFrame(st.session_state.solicitudes).T
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total_solicitudes = len(df)
        st.metric("Total Solicitudes", total_solicitudes)
    with col2:
        aprobadas = len([s for s in st.session_state.solicitudes.values() 
                        if s['aprobaciones']['director']['estado'] == "Aprobado"])
        st.metric("Aprobadas", aprobadas)
    with col3:
        pendientes = len([s for s in st.session_state.solicitudes.values() 
                        if s['aprobaciones']['director']['estado'] == "Pendiente"])
        st.metric("Pendientes", pendientes)
    
    st.markdown("---")  # Separador
    
    # Definir colores base para cada rol
    colores_roles = {
        "Jefe de\nÁrea": "#FF9800",  # Naranja
        "Jefe de\nFinanzas": "#4CAF50",  # Verde
        "Supervisor\nMercado\nPúblico": "#FF9800",  # Naranja
        "Jefe\nAdministrativo": "#4CAF50",  # Verde
        "Director": "#4CAF50"  # Verde
    }
    
    # Contar solicitudes pendientes por nivel
    pendientes_por_nivel = {
        "Jefe de\nÁrea": 0,
        "Jefe de\nFinanzas": 0,
        "Supervisor\nMercado\nPúblico": 0,
        "Jefe\nAdministrativo": 0,
        "Director": 0
    }
    
    # Listas para almacenar detalles de SIC pendientes por nivel
    detalles_pendientes = {
        "Jefe de\nÁrea": [],
        "Jefe de\nFinanzas": [],
        "Supervisor\nMercado\nPúblico": [],
        "Jefe\nAdministrativo": [],
        "Director": []
    }
    
    for num_sic, solicitud in st.session_state.solicitudes.items():
        # Solo contar para Jefe de Área si es del área médica y está pendiente
        if solicitud['area_origen'] == "Área Médica" and solicitud['aprobaciones']['jefe_area']['estado'] == "Pendiente":
            pendientes_por_nivel["Jefe de\nÁrea"] += 1
            detalles_pendientes["Jefe de\nÁrea"].append(num_sic)
        
        # Para Finanzas, contar si:
        # 1. Es del área administrativa o enfermerías y está pendiente
        # 2. Es del área médica, está aprobada por jefe de área y está pendiente
        if ((solicitud['area_origen'] in ["Área Administrativa", "Enfermerías"] and 
             solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente") or
            (solicitud['area_origen'] == "Área Médica" and 
             solicitud['aprobaciones']['jefe_area']['estado'] == "Aprobado" and 
             solicitud['aprobaciones']['finanzas']['estado'] == "Pendiente")):
            pendientes_por_nivel["Jefe de\nFinanzas"] += 1
            detalles_pendientes["Jefe de\nFinanzas"].append(num_sic)
        
        # Para el resto de los niveles, contar solo si el nivel anterior aprobó
        elif solicitud['aprobaciones']['finanzas']['estado'] == "Aprobado":
            if solicitud['aprobaciones']['supervisor']['estado'] == "Pendiente":
                pendientes_por_nivel["Supervisor\nMercado\nPúblico"] += 1
                detalles_pendientes["Supervisor\nMercado\nPúblico"].append(num_sic)
            elif solicitud['aprobaciones']['supervisor']['estado'] == "Aprobado":
                if solicitud['aprobaciones']['jefe_adm']['estado'] == "Pendiente":
                    pendientes_por_nivel["Jefe\nAdministrativo"] += 1
                    detalles_pendientes["Jefe\nAdministrativo"].append(num_sic)
                elif solicitud['aprobaciones']['jefe_adm']['estado'] == "Aprobado":
                    if solicitud['aprobaciones']['director']['estado'] == "Pendiente":
                        pendientes_por_nivel["Director"] += 1
                        detalles_pendientes["Director"].append(num_sic)

    # Mostrar métricas en cards
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, (rol, cantidad) in enumerate(pendientes_por_nivel.items()):
        with cols[i]:
            # Determinar color según cantidad
            if cantidad == 0:
                estado_color = "#4CAF50"  # Verde
                emoji = "✅"
                border_color = "#4CAF50"  # Verde
            elif 1 <= cantidad <= 3:
                estado_color = "#FF9800"  # Naranja
                emoji = "⚠️"
                border_color = "#FF9800"  # Naranja
            else:
                estado_color = "#F44336"  # Rojo
                emoji = "🚨"
                border_color = "#F44336"  # Rojo
            
            # Crear contenedor con color
            with st.container():
                st.markdown(
                    f"""
                    <div style="
                        padding: 15px;
                        border-radius: 5px;
                        border: 2px solid {border_color};
                        background-color: rgba({','.join(map(str, hex_to_rgb(estado_color)))}, 0.1);
                        min-height: 200px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    ">
                        <div>
                            <h4 style="
                                color: {estado_color};
                                margin: 0;
                                white-space: pre-line;
                                line-height: 1.3;
                                font-size: 1.2em;
                            ">{rol} {emoji}</h4>
                        </div>
                        <div style="
                            text-align: center;
                            margin-top: auto;
                            padding-bottom: 10px;
                        ">
                            <div style="
                                font-size: 36px;
                                color: {estado_color};
                                font-weight: bold;
                            ">{cantidad}</div>
                            <div style="
                                font-size: 18px;
                                color: {estado_color};
                            ">pendientes</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# Agregar función auxiliar para convertir colores hex a RGB
def hex_to_rgb(color):
    # Remover el # si existe
    color = color.lstrip('#')
    
    # Convertir el color hexadecimal a RGB
    if len(color) == 6:
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        return (r, g, b)
    
    # Colores predefinidos
    color_map = {
        "#4CAF50": (76, 175, 80),    # Verde
        "#FF9800": (255, 152, 0),    # Naranja
        "#F44336": (244, 67, 54)     # Rojo
    }
    
    return color_map.get(color, (0, 0, 0))

def validar_email(email):
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'  # Acepta cualquier email válido
    return bool(re.match(patron, email))

def administrar_usuarios():
    st.title("Administración de Usuarios")
    
    # Tabla de usuarios existentes
    st.subheader("Usuarios Existentes")
    usuarios_data = []
    for email, data in st.session_state.usuarios.items():
        if email != "admin@ccm.cl":
            usuarios_data.append({
                "Email": email,
                "Rol": data["rol"],
                "Nombre": data["nombre_completo"],
                "Cargo": data["cargo"],
                "Departamento": data["departamento"],
                "Estado": "Activo" if data["activo"] else "Inactivo",
                "Firma": "✅ Registrada" if data.get("firma") else "❌ No registrada"
            })
    
    if usuarios_data:
        df = pd.DataFrame(usuarios_data)
        st.dataframe(df, use_container_width=True)

    # Selector de modo al principio
    modo_edicion = st.radio("Seleccione una acción:", ["Crear Nuevo Usuario", "Editar Usuario Existente"])
    
    if modo_edicion == "Editar Usuario Existente":
        usuario_a_editar = st.selectbox(
            "Seleccionar Usuario para Editar",
            [e for e in st.session_state.usuarios.keys() if e != "admin@ccm.cl"]
        )
        
        if usuario_a_editar:
            datos_usuario = st.session_state.usuarios[usuario_a_editar]
            with st.form("usuario_form"):
                st.subheader(f"Editando usuario: {usuario_a_editar}")
                
                col1, col2 = st.columns(2)
                with col1:
                    nuevo_password = st.text_input("Nueva Contraseña (opcional)", type="password")
                    if nuevo_password:
                        confirmar_password = st.text_input("Confirmar Nueva Contraseña", type="password")
                    
                    nuevo_rol = st.selectbox(
                        "Rol",
                        [
                            "Creador SIC",
                            "Jefe de Área",
                            "Jefe de Finanzas",
                            "Supervisor Mercado Público",
                            "Jefe Administrativo",
                            "Director"
                        ],
                        index=[
                            "Creador SIC",
                            "Jefe de Área",
                            "Jefe de Finanzas",
                            "Supervisor Mercado Público",
                            "Jefe Administrativo",
                            "Director"
                        ].index(datos_usuario["rol"])
                    )  # Cerrar paréntesis del selectbox
                    
                    nuevo_nombre = st.text_input("Nombre Completo", value=datos_usuario["nombre_completo"])
                    nuevo_cargo = st.text_input("Cargo", value=datos_usuario["cargo"])
                    nuevo_departamento = st.text_input("Departamento", value=datos_usuario["departamento"])
                
                with col2:
                    st.subheader("Firma del Usuario")
                    if datos_usuario.get("firma"):
                        st.write("Firma actual:")
                        if datos_usuario["firma"]["tipo"].startswith("image"):
                            st.image(datos_usuario["firma"]["contenido"], width=200)
                    
                    nueva_firma = st.file_uploader(
                        "Subir nueva firma (opcional)",
                        type=['jpg', 'jpeg', 'png'],
                        help="Formatos permitidos: JPG, PNG"
                    )
                
                submitted = st.form_submit_button("Guardar Cambios")
                
                if submitted:
                    if nuevo_password and nuevo_password != confirmar_password:
                        st.error("Las contraseñas no coinciden")
                    else:
                        # Actualizar datos
                        if nuevo_password:
                            datos_usuario["password"] = nuevo_password
                        datos_usuario["rol"] = nuevo_rol
                        datos_usuario["nombre_completo"] = nuevo_nombre
                        datos_usuario["cargo"] = nuevo_cargo
                        datos_usuario["departamento"] = nuevo_departamento
                        
                        if nueva_firma:
                            datos_usuario["firma"] = {
                                "nombre_archivo": nueva_firma.name,
                                "tipo": nueva_firma.type,
                                "contenido": nueva_firma.getvalue()
                            }
                            datos_usuario["activo"] = True
                        
                        st.success("Usuario actualizado exitosamente")
                        st.rerun()
    
    else:  # Crear nuevo usuario
        with st.form("nuevo_usuario_form"):
            st.subheader("Crear Nuevo Usuario")
            
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                confirmar_password = st.text_input("Confirmar Contraseña", type="password")
                rol = st.selectbox("Rol", [
                    "Creador SIC",
                    "Jefe de Área",
                    "Jefe de Finanzas",
                    "Supervisor Mercado Público",
                    "Jefe Administrativo",
                    "Director"
                ])
                nombre_completo = st.text_input("Nombre Completo")
                cargo = st.text_input("Cargo")
                departamento = st.text_input("Departamento")
            
            with col2:
                st.subheader("Firma del Usuario")
                st.write("La firma es obligatoria para activar el usuario")
                firma_archivo = st.file_uploader(
                    "Subir firma digitalizada",
                    type=['jpg', 'jpeg', 'png'],
                    help="Formatos permitidos: JPG, PNG"
                )
            
            submitted = st.form_submit_button("Crear Usuario")
            
            if submitted:
                if not all([email, password, confirmar_password, rol, nombre_completo, cargo, departamento]):
                    st.error("Por favor complete todos los campos")
                elif password != confirmar_password:
                    st.error("Las contraseñas no coinciden")
                elif not validar_email(email):
                    st.error("Por favor ingrese un email válido")
                elif email in st.session_state.usuarios:
                    st.error("Este email ya está registrado")
                elif not firma_archivo:
                    st.error("La firma es obligatoria")
                else:
                    firma_info = {
                        "nombre_archivo": firma_archivo.name,
                        "tipo": firma_archivo.type,
                        "contenido": firma_archivo.getvalue()
                    }
                    
                    st.session_state.usuarios[email] = {
                        "password": password,
                        "rol": rol,
                        "nombre_completo": nombre_completo,
                        "cargo": cargo,
                        "departamento": departamento,
                        "activo": True,
                        "firma": firma_info
                    }
                    
                    st.success(f"Usuario {email} creado exitosamente")
                    st.rerun()

def mostrar_formulario():
    st.sidebar.write(f"Usuario actual: {st.session_state.usuarios[st.session_state.user]['nombre_completo']}")
    if st.sidebar.button("Cerrar Sesión"):
        del st.session_state.user
        del st.session_state.rol
        st.rerun()

    # Mostrar pestañas según el rol
    if st.session_state.rol == "Administrador":
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Resumen", "Gestión de Solicitudes", "Administración"])
        
        with tab1:
            mostrar_dashboard_aprobaciones()
        with tab2:
            mostrar_resumen_solicitudes()
        with tab3:
            revisar_solicitudes()
        with tab4:
            administrar_usuarios()
    else:
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Resumen", "Gestión de Solicitudes"])
        
        with tab1:
            mostrar_dashboard_aprobaciones()
        with tab2:
            mostrar_resumen_solicitudes()
        with tab3:
            if st.session_state.rol == "Creador SIC":
                crear_sic()
            else:
                revisar_solicitudes()

    # Actualizar la pestaña actual
    if tab1:
        st.session_state.current_tab = "Dashboard"
    elif tab2:
        st.session_state.current_tab = "Resumen"
    elif tab3:
        st.session_state.current_tab = "Gestión de Solicitudes"

def main():
    if 'user' not in st.session_state:
        if login():
            crear_solicitudes_ejemplo()  # Crear ejemplos solo al primer inicio
            st.rerun()
    else:
        mostrar_formulario()

def registrar_cambio(accion, usuario, detalles):
    st.session_state.registro_cambios.append({
        "fecha": date.today(),
        "accion": accion,
        "usuario": usuario,
        "detalles": detalles
    })

def generar_cdp(solicitud):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Configuración de márgenes y posiciones
    # Márgenes estándar: 1 pulgada (72 puntos) en todos los lados
    left_margin = 72
    right_margin = 540  # 612 - 72 = 540 (ancho total - margen izquierdo)
    top_margin = 720   # 792 - 72 = 720 (alto total - margen superior)
    
    # Título y encabezado
    c.setFont("Helvetica-Bold", 12)
    c.drawString(left_margin, top_margin, "EJÉRCITO DE CHILE")
    c.drawString(left_margin, top_margin - 20, "DIVISIÓN DE SALUD")
    c.drawString(left_margin, top_margin - 40, "CENTRO CLÍNICO MILITAR COYHAIQUE")
    
    # Nmero de documento y fecha (alineado a la derecha)
    c.setFont("Helvetica", 10)
    c.drawString(right_margin - 200, top_margin, f"CDP N° {solicitud['aprobaciones']['finanzas']['cdp']}")
    c.drawString(right_margin - 200, top_margin - 20, f"COYHAIQUE, {solicitud['fecha'].strftime('%d-%m-%Y')}")
    
    # Título del documento (centrado)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString((right_margin + left_margin)/2, top_margin - 80, "CERTIFICADO DE DISPONIBILIDAD PRESUPUESTARIA")
    
    # Cuerpo del documento
    c.setFont("Helvetica", 10)
    y = top_margin - 120
    line_height = 15  # Altura de línea estándar
    
    texto = f"""
    El Jefe de Finanzas del Centro Clínico Militar "Coyhaique" que suscribe, certifica que:

    De conformidad al presupuesto disponible, conforme a lo que indica la Ley N° 21.640 "Presupuesto 
    para el Sector Público año 2024", se cuenta con los recursos necesarios para financiar la siguiente 
    adquisición:

    N° SIC: {solicitud['num_sic']}
    Descripción: {solicitud['descripcion']}
    Monto Total: ${f"{solicitud['valor_estimado']:,.0f}".replace(",", ".")}
    Tipo de Compra: {solicitud['tipo_compra']}
    """
    
    # Agregar catálogos si existen
    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
        texto += "\n\nDistribución presupuestaria:"
        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
            if catalogo['numero'] and catalogo['monto'] > 0:
                texto += f"\n{catalogo['numero']}: ${catalogo['monto']:,.0f}".replace(",", ".")
    
    # Escribir el texto línea por línea respetando los saltos
    lineas = texto.strip().split('\n')
    for linea in lineas:
        if linea.strip():  # Si la línea tiene contenido
            c.drawString(left_margin, y, linea.strip())
            y -= line_height
        else:  # Si la línea está vacía (salto de línea)
            y -= line_height  # Agregar espacio adicional
    
    # Sección de firma (centrada en la parte inferior)
    y = 200  # Posición fija para la sección de firma
    c.drawString(left_margin, y, "Se extiende el presente certificado para los fines que correspondan.")
    
    # Línea y datos de firma centrados
    firma_x = (right_margin + left_margin)/2
    y -= 60
    
    # Si hay firma digitalizada, agregarla (centrada)
    if 'firma' in st.session_state.usuarios['finanzas@ccm.cl']:
        firma = st.session_state.usuarios['finanzas@ccm.cl']['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Ajustar espaciado de la firma
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, f"{st.session_state.usuarios['finanzas@ccm.cl']['nombre_completo']}")
    c.drawCentredString(firma_x, y - 55, "Jefe de Finanzas CCM 'Coyhaique'")
    
    c.save()
    buffer.seek(0)
    return buffer

def mostrar_cdp(solicitud):
    buffer = generar_cdp(solicitud)
    st.download_button(
        label="Descargar CDP",
        data=buffer,
        file_name=f"CDP_{solicitud['num_sic']}.pdf",
        mime="application/pdf"
    )

def agregar_linea_divisoria(c, y, left_margin, right_margin):
    """Función auxiliar para dibujar línea divisoria"""
    c.setLineWidth(0.5)  # Línea delgada
    c.line(left_margin, y, right_margin, y)  # Línea horizontal
    return y - 10  # Retorna nueva posición Y con espacio adicional

def generar_resumen_sic(solicitud):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=LEGAL)
    
    # Configuración de márgenes más ajustados
    left_margin = 40  # Reducido para más espacio horizontal
    right_margin = 572  # Ajustado al ancho
    top_margin = 980  # Ajustado a la altura
    
    # Encabezado
    c.setFont("Helvetica-Bold", 10)
    c.drawString(left_margin, top_margin, "EJÉRCITO DE CHILE")
    c.drawString(left_margin + 200, top_margin, f"N° SIC: {solicitud['num_sic']}")
    c.drawString(left_margin, top_margin - 15, "DIVISIÓN DE SALUD")
    c.drawString(left_margin + 200, top_margin - 15, f"FECHA: {solicitud['fecha'].strftime('%d-%m-%Y')}")
    c.drawString(left_margin, top_margin - 30, "CENTRO CLÍNICO MILITAR COYHAIQUE")
    
    # Título
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString((right_margin + left_margin)/2, top_margin - 50, "SOLICITUD INTERNA DE COMPRA")
    
    # Configuración de la tabla
    y = top_margin - 80
    col_width = (right_margin - left_margin) / 3
    row_height = 12  # Reducido para más compacto
    
    def add_row(label1, value1, label2="", value2="", label3="", value3=""):
        nonlocal y
        # Primera columna
        c.setFont("Helvetica-Bold", 8)
        c.drawString(left_margin, y, label1)
        c.setFont("Helvetica", 8)
        c.drawString(left_margin + 80, y, str(value1))
        
        # Segunda columna
        if label2:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(left_margin + col_width + 10, y, label2)
            c.setFont("Helvetica", 8)
            c.drawString(left_margin + col_width + 90, y, str(value2))
        
        # Tercera columna
        if label3:
            c.setFont("Helvetica-Bold", 8)
            c.drawString(left_margin + 2*col_width + 10, y, label3)
            c.setFont("Helvetica", 8)
            c.drawString(left_margin + 2*col_width + 90, y, str(value3))
        
        y -= row_height
    
    # Solo información del creador
    add_row("SOLICITANTE:", solicitud['creador']['nombre'], 
            "ÁREA:", solicitud['area_origen'],
            "TIPO DE COMPRA:", solicitud['tipo_compra'])
    
    if solicitud['tipo_compra'] == "Licitación Pública":
        add_row("N° LICITACIÓN:", solicitud['licitacion_num'],
                "SALDO:", f"${solicitud['saldo']:,.0f}".replace(",", "."),
                "VALOR EST.:", f"${solicitud['valor_estimado']:,.0f}".replace(",", "."))
        add_row("PROVEEDOR:", solicitud['nombre_proveedor'],
                "RUT:", solicitud['rut_proveedor'])
    else:
        add_row("VALOR ESTIMADO:", f"${solicitud['valor_estimado']:,.0f}".replace(",", "."))
    
    add_row("CONFLICTO:", solicitud['creador']['conflicto_interes']['tiene_conflicto'])
    if solicitud['creador']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['creador']['conflicto_interes']['detalle'])
    
    # Descripción y motivo
    y -= 10
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left_margin, y, "DESCRIPCIÓN:")
    y -= row_height
    c.setFont("Helvetica", 8)
    c.drawString(left_margin + 10, y, solicitud['descripcion'])
    
    y -= 20
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left_margin, y, "MOTIVO:")
    y -= row_height
    c.setFont("Helvetica", 8)
    c.drawString(left_margin + 10, y, solicitud['motivo'])
    
    # Firma del creador
    y -= 40
    firma_x = right_margin - 100
    
    # Obtener datos del creador
    email_creador = next(email for email, data in st.session_state.usuarios.items() 
                        if data['nombre_completo'] == solicitud['creador']['nombre'])
    datos_creador = st.session_state.usuarios[email_creador]
    
    # Si hay firma digitalizada
    if 'firma' in datos_creador:  # Cambiado datos_usuario por datos_creador
        firma = datos_creador['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_creador['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_creador['cargo'])
    
    # Agregar línea divisoria después del cargo del creador
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)
    
    # Información del Jefe de Área en tres columnas
    add_row("JEFE DE ÁREA:", solicitud['aprobaciones']['jefe_area']['estado'], 
            "FECHA:", solicitud['fecha'].strftime('%d-%m-%Y'),
            "CONFLICTO:", solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto'])
    
    if solicitud['aprobaciones']['jefe_area']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['aprobaciones']['jefe_area']['conflicto_interes']['detalle'])
    
    # Comentario en una línea separada
    if solicitud['aprobaciones']['jefe_area']['comentario']:
        add_row("COMENTARIO:", solicitud['aprobaciones']['jefe_area']['comentario'])
    
    # Firma del Jefe de Área
    y -= 20  # Reducido de 40 a 20 para disminuir el espacio
    firma_x = right_margin - 100  # Cambiado de 150 a 100 para mover más a la derecha
    
    # Obtener datos del Jefe de Área
    email_jefe = next(email for email, data in st.session_state.usuarios.items() 
                     if data['rol'] == "Jefe de Área")
    datos_jefe = st.session_state.usuarios[email_jefe]
    
    # Si hay firma digitalizada
    if 'firma' in datos_jefe:
        firma = datos_jefe['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)  # Centrar la imagen respecto al nuevo punto
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_jefe['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_jefe['cargo'])
    
    # Agregar línea divisoria después del cargo
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)  # Ajustado de y - 20 a y - 75
    
    # En la sección del Jefe de Finanzas
    add_row("JEFE DE FINANZAS:", solicitud['aprobaciones']['finanzas']['estado'], 
            "FECHA:", solicitud['fecha'].strftime('%d-%m-%Y'),
            "CONFLICTO:", solicitud['aprobaciones']['finanzas']['conflicto_interes']['tiene_conflicto'])
    
    # Agregar N° CDP
    add_row("N° CDP:", solicitud['aprobaciones']['finanzas']['cdp'])
    
    # Agregar título de distribución presupuestaria
    c.setFont("Helvetica-Bold", 8)
    c.drawString(left_margin, y, "DISTRIBUCIÓN PRESUPUESTARIA:")
    y -= row_height
    
    # Mostrar catálogos con formato mejorado
    if 'catalogos' in solicitud['aprobaciones']['finanzas']:
        for catalogo in solicitud['aprobaciones']['finanzas']['catalogos']:
            if catalogo['numero'] and catalogo['monto'] > 0:
                add_row(catalogo['numero'], "", 
                       "MONTO:", f"${catalogo['monto']:,.0f}".replace(",", "."))
    
    if solicitud['aprobaciones']['finanzas']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['aprobaciones']['finanzas']['conflicto_interes']['detalle'])
    
    # Comentario en una línea separada
    if solicitud['aprobaciones']['finanzas']['comentario']:
        add_row("COMENTARIO:", solicitud['aprobaciones']['finanzas']['comentario'])
    
    # Firma del Jefe de Finanzas
    y -= 20  # Espacio reducido antes de la firma
    firma_x = right_margin - 100  # Cambiado de 150 a 100 para mover más a la derecha
    
    # Obtener datos del Jefe de Finanzas
    email_finanzas = next(email for email, data in st.session_state.usuarios.items() 
                         if data['rol'] == "Jefe de Finanzas")
    datos_finanzas = st.session_state.usuarios[email_finanzas]
    
    # Si hay firma digitalizada
    if 'firma' in datos_finanzas:
        firma = datos_finanzas['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)  # Centrar la imagen respecto al nuevo punto
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_finanzas['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_finanzas['cargo'])
    
    # Agregar línea divisoria después del cargo
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)  # Ajustado de y - 20 a y - 75
    
    # Información del Supervisor en tres columnas
    add_row("SUPERVISOR:", solicitud['aprobaciones']['supervisor']['estado'], 
            "FECHA:", solicitud['fecha'].strftime('%d-%m-%Y'),
            "CONFLICTO:", solicitud['aprobaciones']['supervisor']['conflicto_interes']['tiene_conflicto'])
    
    if solicitud['aprobaciones']['supervisor']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['aprobaciones']['supervisor']['conflicto_interes']['detalle'])
    
    # Comentario en una línea separada
    if solicitud['aprobaciones']['supervisor']['comentario']:
        add_row("COMENTARIO:", solicitud['aprobaciones']['supervisor']['comentario'])
    
    # Firma del Supervisor
    y -= 20  # Espacio reducido antes de la firma
    firma_x = right_margin - 100  # Cambiado de 150 a 100 para mover más a la derecha
    
    # Obtener datos del Supervisor
    email_supervisor = next(email for email, data in st.session_state.usuarios.items() 
                          if data['rol'] == "Supervisor Mercado Público")
    datos_supervisor = st.session_state.usuarios[email_supervisor]
    
    # Si hay firma digitalizada
    if 'firma' in datos_supervisor:
        firma = datos_supervisor['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)  # Centrar la imagen respecto al nuevo punto
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_supervisor['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_supervisor['cargo'])
    
    # Agregar línea divisoria después del cargo
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)  # Ajustado de y - 20 a y - 75
    
    # Información del Jefe Administrativo en tres columnas
    add_row("JEFE ADMINISTRATIVO:", solicitud['aprobaciones']['jefe_adm']['estado'], 
            "FECHA:", solicitud['fecha'].strftime('%d-%m-%Y'),
            "CONFLICTO:", solicitud['aprobaciones']['jefe_adm']['conflicto_interes']['tiene_conflicto'])
    
    if solicitud['aprobaciones']['jefe_adm']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['aprobaciones']['jefe_adm']['conflicto_interes']['detalle'])
    
    # Comentario en una línea separada
    if solicitud['aprobaciones']['jefe_adm']['comentario']:
        add_row("COMENTARIO:", solicitud['aprobaciones']['jefe_adm']['comentario'])
    
    # Firma del Jefe Administrativo
    y -= 20  # Espacio reducido antes de la firma
    firma_x = right_margin - 100  # Cambiado de 150 a 100 para mover más a la derecha
    
    # Obtener datos del Jefe Administrativo
    email_jefe_adm = next(email for email, data in st.session_state.usuarios.items() 
                         if data['rol'] == "Jefe Administrativo")
    datos_jefe_adm = st.session_state.usuarios[email_jefe_adm]
    
    # Si hay firma digitalizada
    if 'firma' in datos_jefe_adm:
        firma = datos_jefe_adm['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)  # Centrar la imagen respecto al nuevo punto
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_jefe_adm['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_jefe_adm['cargo'])
    
    # Agregar línea divisoria después del cargo
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)  # Ajustado de y - 20 a y - 75
    
    # Información del Director en tres columnas
    add_row("DIRECTOR:", solicitud['aprobaciones']['director']['estado'], 
            "FECHA:", solicitud['fecha'].strftime('%d-%m-%Y'),
            "CONFLICTO:", solicitud['aprobaciones']['director']['conflicto_interes']['tiene_conflicto'])
    
    if solicitud['aprobaciones']['director']['conflicto_interes']['tiene_conflicto'] == "Sí":
        add_row("DETALLE CONFLICTO:", solicitud['aprobaciones']['director']['conflicto_interes']['detalle'])
    
    # Comentario en una línea separada
    if solicitud['aprobaciones']['director']['comentario']:
        add_row("COMENTARIO:", solicitud['aprobaciones']['director']['comentario'])
    
    # Firma del Director
    y -= 20  # Espacio reducido antes de la firma
    firma_x = right_margin - 100  # Cambiado de 150 a 100 para mover más a la derecha
    
    # Obtener datos del Director
    email_director = next(email for email, data in st.session_state.usuarios.items() 
                         if data['rol'] == "Director")
    datos_director = st.session_state.usuarios[email_director]
    
    # Si hay firma digitalizada
    if 'firma' in datos_director:
        firma = datos_director['firma']
        if firma and firma['tipo'].startswith('image'):
            img = ImageReader(io.BytesIO(firma['contenido']))
            firma_width = 120
            firma_height = 60
            img_x = firma_x - (firma_width/2)  # Centrar la imagen respecto al nuevo punto
            img_y = y - 20
            c.drawImage(img, img_x, img_y, width=firma_width, height=firma_height)
    
    # Línea, nombre y cargo alineados a la derecha
    c.drawCentredString(firma_x, y - 20, "_____________________________")
    c.drawCentredString(firma_x, y - 40, datos_director['nombre_completo'])
    c.drawCentredString(firma_x, y - 55, datos_director['cargo'])
    
    # Agregar línea divisoria después del cargo
    y = agregar_linea_divisoria(c, y - 75, left_margin, right_margin)  # Ajustado de y - 20 a y - 75
    
    c.save()
    buffer.seek(0)
    return buffer

if __name__ == "__main__":
    main()

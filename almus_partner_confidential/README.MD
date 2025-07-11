# Almus - Información Confidencial de Contactos

## Descripción

Este módulo para Odoo 18 permite gestionar información confidencial de proveedores y contactos mediante una pestaña especial con control de acceso basado en permisos. La funcionalidad puede ser activada o desactivada desde el panel de configuración de Almus.

## Características Principales

- ✅ **Pestaña "Información Confidencial"** en el formulario de contactos
- ✅ **Control de acceso granular** mediante grupos de seguridad
- ✅ **Activación/desactivación** desde configuración sin necesidad de desinstalar
- ✅ **Búsquedas optimizadas** con campo indexado
- ✅ **Sin campos computados** para mejor rendimiento
- ✅ **Caché inteligente** para optimizar la carga de vistas

## Instalación

1. Copiar la carpeta `almus_partner_confidential` en el directorio de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Buscar "Almus Información Confidencial"
4. Instalar el módulo

## Configuración

### Activar la funcionalidad

1. Ir a **Configuración → Ajustes → Almus Dev**
2. En la sección "Información Confidencial de Contactos"
3. Marcar "Activar Información Confidencial"
4. Guardar

### Otorgar permisos a usuarios

**Importante**: Los administradores del sistema NO tienen acceso automático a la información confidencial.

1. Ir a **Configuración → Usuarios y Compañías → Usuarios**
2. Seleccionar el usuario
3. En la pestaña "Permisos de Acceso"
4. Buscar la sección "Información Confidencial de Contactos"
5. Asignar uno de estos permisos:
   - **Ver Información Confidencial**: Solo lectura
   - **Administrar Información Confidencial**: Lectura y escritura

## Campos Disponibles

### Datos de Contacto Internacional
- **Nombre Internacional**: Nombre en idioma original o comercial
- **Correo Confidencial**: Email privado para comunicaciones sensibles
- **WeChat ID**: Identificador de WeChat
- **WhatsApp**: Número para comunicaciones directas
- **Persona de Contacto Clave**: Contacto principal para asuntos importantes

### Información Comercial
- **Términos de Pago Especiales**: Condiciones negociadas
- **Condiciones de Precios**: Descuentos y precios especiales
- **Información Bancaria**: Datos para transferencias internacionales
- **Información de Crédito**: Límites y referencias comerciales
- **Notas Internas Confidenciales**: Información privada del proveedor

## Funcionalidades Técnicas

### Optimización de Rendimiento
- **Caché de vistas**: Las vistas se cachean para evitar procesamiento repetido
- **Campo indexado**: `almus_has_confidential` para búsquedas rápidas
- **Sin campos computados**: Mejor rendimiento en bases de datos grandes

### Seguridad
- Control de acceso basado en grupos
- Validación de permisos en create/write
- Los campos confidenciales se eliminan automáticamente si la funcionalidad está desactivada

### Búsquedas
- Filtro "Con Info Confidencial" optimizado
- Indicador visual en vista de lista
- Búsqueda rápida mediante campo booleano indexado

## Comportamiento del Sistema

- **Funcionalidad activada**: La pestaña es visible para usuarios con permisos
- **Funcionalidad desactivada**: La pestaña desaparece completamente para todos
- **Sin permisos**: Los usuarios no ven la pestaña ni pueden acceder a los datos
- **Solo lectura**: Los usuarios pueden ver pero no editar la información
- **Lectura/Escritura**: Control total sobre la información confidencial

## Estructura del Módulo

```
almus_partner_confidential/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── res_partner.py          # Modelo con campos y lógica
│   └── res_config_settings.py  # Configuración del módulo
├── security/
│   ├── almus_partner_confidential_security.xml  # Grupos de seguridad
│   └── ir.model.access.csv                      # Permisos de acceso
└── views/
    ├── res_config_settings_views.xml  # Vista de configuración
    └── res_partner_views.xml          # Vistas del contacto
```

## Notas Importantes

- La información confidencial NO se elimina al desactivar el módulo
- Los datos permanecen en la base de datos pero no son accesibles
- Al reactivar, la información vuelve a estar disponible
- El módulo registra en logs las modificaciones para auditoría

## Compatibilidad

- **Odoo**: 18.0
- **Dependencias**: almus_base, base, contacts
- **Licencia**: LGPL-3

## Soporte

Desarrollado por [Almus Dev](https://www.almus.dev)

Para soporte o consultas, contactar a través del sitio web.

## Changelog

### Versión 18.0.1.0.0
- Versión inicial con funcionalidad completa
- Optimización de rendimiento con caché
- Campo indexado para búsquedas rápidas
- Eliminación de campos de auditoría
- Control de activación/desactivación mejorado
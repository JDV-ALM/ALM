# Almus Product Category per Company

## Descripción

Este módulo modifica el comportamiento estándar de Odoo para que las categorías de producto sean específicas por empresa en lugar de globales. Permite que cada empresa en un entorno multi-empresa tenga su propio conjunto de categorías de productos independientes.

## Características

- **Categorías por Empresa**: Cada categoría de producto puede asignarse a una empresa específica
- **Filtrado Automático**: Los usuarios solo ven las categorías de su empresa actual
- **Categorías Compartidas**: Opción de crear categorías sin empresa para compartir entre todas
- **Migración Automática**: Al activar, asigna automáticamente las categorías existentes a la empresa actual
- **Activación/Desactivación**: Se puede habilitar o deshabilitar desde Configuración → Almus Dev
- **Reglas de Seguridad**: Aplica restricciones de acceso solo cuando está habilitado
- **Validaciones**: Asegura que las categorías padre e hijo pertenezcan a la misma empresa

## Requisitos

- Odoo 18.0+
- Módulo `almus_base` instalado
- Módulo `product` (incluido en Odoo)

## Instalación

1. Asegúrate de tener instalado `almus_base`
2. Copia este módulo en tu directorio de addons
3. Actualiza la lista de aplicaciones
4. Instala el módulo "Almus Product Category per Company"

## Configuración

### Activación

1. Ve a **Configuración → Ajustes**
2. Busca la sección **Almus Dev**
3. Encuentra "Categorías de Producto por Empresa"
4. Activa la casilla para habilitar la funcionalidad

### Uso

Una vez activado:

- Al crear nuevas categorías, se asignarán automáticamente a tu empresa actual
- Puedes cambiar la empresa de una categoría desde el formulario (si tienes permisos multi-empresa)
- Las categorías sin empresa serán visibles para todas las empresas
- En la vista de búsqueda, puedes filtrar por "Mi Empresa" o "Categorías Compartidas"

### Desactivación

Para desactivar la funcionalidad:

1. Ve a **Configuración → Ajustes → Almus Dev**
2. Desactiva la casilla "Categorías de Producto por Empresa"
3. Las reglas de seguridad se desactivarán pero los datos de empresa en las categorías se mantendrán

## Comportamiento Técnico

### Cuando está ACTIVADO:

- Las nuevas categorías se crean con `company_id = empresa_actual`
- Se aplican reglas de seguridad que filtran categorías por empresa
- Las categorías padre e hijo deben pertenecer a la misma empresa
- El método `_search` filtra automáticamente por empresa
- En contexto multi-empresa, el nombre muestra `[Empresa]` al final

### Cuando está DESACTIVADO:

- Comportamiento estándar de Odoo (categorías globales)
- No se aplica ningún filtrado por empresa
- No se validan restricciones de empresa padre/hijo
- Las reglas de seguridad están inactivas

## Migraciones

Al activar por primera vez, el módulo:

1. Asigna todas las categorías sin empresa a la empresa actual
2. Activa las reglas de seguridad
3. Registra la migración en los logs del sistema

## Permisos

- **Usuarios normales**: Solo ven categorías de su empresa actual y las compartidas
- **Usuarios multi-empresa**: Ven categorías de todas sus empresas permitidas
- **Administradores**: Pueden gestionar categorías de cualquier empresa

## Casos de Uso

### Caso 1: Empresa con múltiples sucursales
Cada sucursal puede tener su propia estructura de categorías sin interferir con las demás.

### Caso 2: Holding empresarial
Cada empresa del grupo mantiene su catálogo de productos organizado independientemente.

### Caso 3: Franquicias
La central puede definir categorías compartidas mientras cada franquicia tiene las suyas propias.

## Solución de Problemas

### Las categorías no se filtran por empresa
- Verifica que el módulo esté activado en Configuración → Almus Dev
- Comprueba que las reglas de seguridad estén activas
- Revisa que el usuario no sea superadministrador

### Error al crear categoría hijo
- Asegúrate que la categoría padre pertenezca a la misma empresa
- Si la categoría padre no tiene empresa, la hija tampoco debe tenerla

### No veo la opción en configuración
- Verifica que `almus_base` esté instalado
- Actualiza la lista de módulos
- Revisa los logs en busca de errores de instalación

## Soporte

Para soporte técnico o consultas sobre este módulo:
- Email: info@almus.dev
- Web: https://www.almus.dev

## Licencia

LGPL-3

---

Desarrollado por [Almus Dev](https://www.almus.dev)
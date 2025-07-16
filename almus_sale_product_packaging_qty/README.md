# Almus Sale Product Packaging Quantity

## Descripción

Módulo de Odoo 18 desarrollado por **Almus Dev** que agrega información de cantidad por empaque en la vista de catálogo de productos dentro del formulario de ventas.

## Problema Resuelto

Durante el proceso de ventas, los usuarios no podían visualizar la cantidad de unidades por empaque directamente en el catálogo de productos, lo que generaba:
- Confusión en los volúmenes solicitados
- Posibles errores en el control de stock
- Necesidad de buscar información adicional fuera del flujo de trabajo

## Características

- ✅ Campo entero de solo lectura para cantidad por empaque
- ✅ Visualización clara en la vista kanban del catálogo
- ✅ Configurable desde el panel de Almus Dev
- ✅ Sin campos computados (mejor rendimiento)
- ✅ Integración con el ecosistema Almus

## Instalación

1. Copiar la carpeta `almus_sale_product_packaging_qty` en el directorio de addons de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo "Almus Sale Product Packaging Quantity"

## Configuración

### Activar/Desactivar la funcionalidad

1. Ir a **Configuración → Ajustes → Almus Dev**
2. En la sección "Cantidad por Empaque en Ventas", activar o desactivar según necesidad

### Configurar cantidad por empaque en productos

1. Ir a **Ventas → Productos → Productos**
2. Abrir el producto deseado
3. En la pestaña "Inventario", sección "Logística"
4. Configurar el campo "Cantidad por Empaque"

## Uso

Una vez configurado, la información aparecerá automáticamente en:
- Vista de catálogo de productos en órdenes de venta
- Vista lista de productos (columna opcional)
- Formulario del producto

La cantidad por empaque se mostrará solo cuando sea mayor a 1 unidad.

## Dependencias

- `almus_base`: Módulo base del ecosistema Almus
- `sale`: Módulo de ventas de Odoo
- `product`: Módulo de productos de Odoo

## Versión

- **Versión**: 18.0.1.0.0
- **Compatible con**: Odoo 18.0
- **Licencia**: LGPL-3

## Autor

**Almus Dev**  
[www.almus.dev](https://www.almus.dev)

## Soporte

Para soporte o consultas, contactar a través del sitio web de Almus Dev.

---

*Desarrollado siguiendo las mejores prácticas del ecosistema Almus*
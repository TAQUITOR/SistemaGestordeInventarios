import pandas as pd
import streamlit as st
import plotly.express as px
import time
from PIL import Image
import os
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt


# ################# FUNCIONES ################### #

def crearTabla(hoja):
    df_tabla = pd.read_excel(excel_file, sheet_name=hoja)
    return df_tabla

@st.cache_data
def load_data(sheet_name):
    return pd.read_excel(excel_file, sheet_name=sheet_name)

def aplicarFormatoChart(fig,controls=False,legend=False,hoverTemplate=None):
    fig.update_layout(
        paper_bgcolor='#f0f4f8',  # Color de fondo del papel
        plot_bgcolor='#f0f4f8',  # Color de fondo de la gráfica
        showlegend=legend,  # Mostrar la leyenda si está activado
        title_pad_l=20,  # Padding para el título
        title_font=dict(  # Configuración del título
            family="verdana",
            color="black",  # Color del texto del título
            size=20
        ),
        font=dict(
            family="Open Sans",  # Fuente para todos los textos
            color="darkblue",  # Color de todos los textos
            size=15
        ),
        legend=dict(
            title=dict(font=dict(color="darkblue"))  # Color del título de la leyenda
        ),
        xaxis=dict(
            tickfont=dict(color="#333"),  # Color de las etiquetas del eje x
        ),
        yaxis=dict(
            tickfont=dict(color="#333"),  # Color de las etiquetas del eje y
        )
    )
    return fig

color_discrete_sequence=["#1ea47e","#e33f2b",'#fbac5d','#82858d','#4ce1ee','#ffa111']

st.set_page_config(layout="wide", page_title="Inventarios 2023")

# ####
tabs = ['Inicio', 'Inventario', 'Ventas','Copilot Express', 'Ayuda y Soporte']


st.sidebar.image("Logo2.png")


# ################# SIDEBAR CONFIG ################### #

with st.sidebar:
    selected_tab = option_menu(
        menu_title="Menu",
        options=tabs,
        icons=["house", "bookshelf", "currency-dollar", "c-circle-fill", "gear", "person-raised-hand"]
    )

# ################# COMMUNICATION WITH EXCEL ################### #


# --- Cargando dataframe , leyendo archivo de excel --- #
excel_file = "C:\\Users\\diego\\Escritorio\\WebAPP_Proyect\\Inventarios.xlsx"

# ################# COMUNICACION CON CSS ################### #

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)



# ############################## ESTRUCTURA DE PAGINA ###################################

if selected_tab == 'Inicio':
    st.header('Bienvenido al Dashboard')

    # Cargando data frames
    df_inventario = load_data("Inventario")
    df_ventas = load_data("Ventas")

    # Calculo de KPI's

    cantidadProductos = df_inventario['Cantidad en Stock'].sum()
    productosVendidos = df_ventas['Cantidad Vendida'].sum()
    ventastotales = df_ventas['Total Venta'].sum()
    first_column, second_column, third_column = st.columns(3)

    with first_column:
        st.markdown(
            '<div class="kpi-container"><div class="kpi-label">Stock Total</div><div class="kpi-value">{}</div></div>'.format(
                cantidadProductos),
            unsafe_allow_html=True
        )

    with second_column:
        st.markdown(
            '<div class="kpi-container"><div class="kpi-label">Ventas Totales</div><div class="kpi-value">{}</div></div>'.format(
                productosVendidos),
            unsafe_allow_html=True
        )

    with third_column:
        nivel_critico = 10  # Define el nivel crítico según tus necesidades
        productos_criticos = df_inventario[df_inventario['Cantidad en Stock'] < nivel_critico].shape[0]
        st.markdown(
            '<div class="kpi-container"><div class="kpi-label">Stock Bajo</div><div class="kpi-value">{}</div></div>'.format(
                productos_criticos),
            unsafe_allow_html=True
        )

    first_chart, second_chart= st.columns(2)

    with first_chart:
        cantidad_vendida_producto = df_ventas.groupby(by=["Producto"])[["Cantidad Vendida"]].sum().sort_values(
            by=["Cantidad Vendida"], ascending=False)

        top10 = cantidad_vendida_producto.head(10)
        # Crear la gráfica de barras
        config_Grafica = px.bar(
            top10.reset_index(),  # Resetear el índice para usar 'Producto' como columna
            y="Producto",
            x="Cantidad Vendida",
            title="Cantidad Vendida por Producto",
            labels={"Producto": "Producto", "Cantidad Vendida": "Cantidad Vendida"},
            color= "Producto"

        )

        st.plotly_chart(aplicarFormatoChart(config_Grafica), use_container_width=True)
        #st.plotly_chart(config_Grafica)

    with second_chart:

        fig = px.pie(df_inventario.head(10), values='Cantidad en Stock', names='Nombre de Producto', hole=0.4,
                     title='TOP 10 CANTIDAD EN STOCK')

        # Mostrar la gráfica en Streamlit
        #st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(aplicarFormatoChart(fig, controls=True), use_container_width=True)

    kpicolumn1, kpicolumn2 = st.columns(2)

    with kpicolumn1:
        valor_total_inventario = (df_inventario['Cantidad en Stock'] * df_inventario['Precio Unitario']).sum()
        st.markdown(
            '<div class="kpi-container"><div class="kpi-label">Valor de Inventario</div><div class="kpi-value">${:,.2f}</div></div>'.format(
                valor_total_inventario),
            unsafe_allow_html=True
        )

    with kpicolumn2:
        producto_mas_vendido = df_ventas.groupby('Producto')['Cantidad Vendida'].sum().idxmax()

        st.markdown(
            '<div class="kpi-container"><div class="kpi-label">Producto mas Vendido</div><div class="kpi-value">{}</div></div>'.format(
                producto_mas_vendido),
            unsafe_allow_html=True
        )

elif selected_tab == 'Inventario':

    df_inventario = load_data("Inventario")

    st.header('Inventario')
    sub_tabs = ['Tabla de Inventario', 'Historial de Inventario']

    tabInventario, tabHistorial = st.tabs(sub_tabs)

    with tabInventario:
        df = load_data("Inventario")
        st.subheader('Tabla de Inventario')
        # Cargar y mostrar la tabla de inventario aquí
        st.dataframe(df_inventario)

        fig_cantidad = px.bar(
            df,
            x='Nombre de Producto',
            y='Cantidad en Stock',
            title='Cantidad por Producto',
            labels={'Cantidad': 'Cantidad'}
        )

        df['Valor de Inventario'] = df['Cantidad en Stock'] * df['Valor de Inventario']
        fig_valor_total = px.bar(
            df,
            x='Nombre de Producto',
            y='Valor de Inventario',
            title='Valor Total por Producto',
            labels={'Valor Total': 'Valor Total'}
        )

        st.plotly_chart(fig_valor_total)

        fig = px.bar(df, x='Nombre de Producto', y=['Cantidad en Stock', 'Valor de Inventario'],
                     title='Cantidad en Stock y Valor de Inventario por Producto',
                     labels={'value': 'Cantidad / Valor', 'variable': 'Tipo'})
        #aplicarFormatoChart(fig)
        st.plotly_chart(fig)

        df_reorder = df['Cantidad en Stock'] < df['Reorder level']
        fig = px.pie(df, names=['Por Debajo del Nivel de Reorden', 'Por Encima del Nivel de Reorden'],
                     values=[df_reorder.sum(), (~df_reorder).sum()],
                     title='Proporción de Productos por Nivel de Reorden')
        #aplicarFormatoChart(fig)
        st.plotly_chart(fig)

        fig = px.density_heatmap(df, x='Precio Unitario', y='Cantidad en Stock',
                                 title='Mapa de Calor: Precio Unitario vs Cantidad en Stock')
        #aplicarFormatoChart(fig)
        st.plotly_chart(fig)

    with tabHistorial:
        df_historial = load_data("HistorialVentas")
        st.subheader('Historial de Inventario')

        # Filtros en la barra lateral
        st.sidebar.subheader("Filtros")

        # Selección de rango de fechas
        filtro_fecha = st.sidebar.date_input("Seleccionar rango de fechas", [])
        # Asegurarse de que 'Fecha' en df_historial esté en formato datetime.date
        df_historial['Fecha'] = pd.to_datetime(df_historial['Fecha']).dt.date

        # Selección de producto con opción de "Todos"
        opciones_producto = ["Todos"] + list(df_historial['Producto'].unique())
        filtro_producto = st.sidebar.selectbox("Seleccionar producto", opciones_producto)

        # Aplicar filtros
        if filtro_fecha:
            # Asegurarse de que haya un rango de fechas completo seleccionado
            if len(filtro_fecha) == 2:
                df_historial = df_historial[
                    (df_historial['Fecha'] >= filtro_fecha[0]) & (df_historial['Fecha'] <= filtro_fecha[1])
                    ]

        if filtro_producto != "Todos":
            df_historial = df_historial[df_historial['Producto'] == filtro_producto]

        # Mostrar tabla de historial
        st.dataframe(df_historial)

        # Gráfico de movimientos de inventario
        df_historial['Fecha'] = pd.to_datetime(df_historial['Fecha'])
        movimientos_por_fecha = df_historial.groupby(df_historial['Fecha'].dt.to_period('M')).sum(numeric_only=True)
        grafica_movimientos = px.line(
            movimientos_por_fecha,
            x=movimientos_por_fecha.index.astype(str),
            y="Cantidad",
            title="Movimientos de Inventario a lo Largo del Tiempo",
            labels={"x": "Fecha", "Cantidad": "Cantidad Movida"}
        )
        st.plotly_chart(grafica_movimientos, use_container_width=True)

elif selected_tab == 'Ventas':

    df_ventas = load_data("Ventas")

    st.header('Ventas')
    st.subheader('Historial de Ventas')
    st.dataframe(df_ventas)

    total_ventas = df_ventas['Total Venta'].sum()
    producto_mas_vendido = df_ventas.groupby('Producto')['Cantidad Vendida'].sum().idxmax()

    kpi1, kpi2 = st.columns(2)
    with kpi1:
        st.subheader("Total de Ventas")
        st.subheader(f"${total_ventas:,.2f}")

    with kpi2:
        st.subheader("Producto Más Vendido")
        st.subheader(producto_mas_vendido)


    chartventas1, chartventas2 = st.columns(2)

    with chartventas1:
        df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
        ventas_mensuales = df_ventas.resample('M', on='Fecha').sum()
        fig_bar = px.bar(ventas_mensuales, x=ventas_mensuales.index, y='Total Venta', title="Ventas Mensuales")
        st.plotly_chart(fig_bar)

        # Gráfico de líneas - Tendencia de Ventas
        fig_line = px.line(ventas_mensuales, x=ventas_mensuales.index, y='Total Venta', title="Tendencia de Ventas")
        st.plotly_chart(fig_line)

    with chartventas2:

        # Filtrar productos con ventas significativas
        umbral_ventas = 1000000  # Ajusta este valor según sea necesario
        ventas_por_producto = df_ventas.groupby('Producto')['Total Venta'].sum()
        ventas_filtradas = ventas_por_producto[ventas_por_producto > umbral_ventas]

        fig_pie = px.pie(ventas_filtradas, values='Total Venta', names=ventas_filtradas.index,
                         title="Distribución de Ventas por Producto ")
        st.plotly_chart(fig_pie)

        # ventas_por_producto = df_ventas.groupby('Producto')['Total Venta'].sum()
        # fig_pie = px.pie(ventas_por_producto, values='Total Venta', names=ventas_por_producto.index,
        #                  title="Distribución de Ventas por Producto")
        # st.plotly_chart(fig_pie)



        # Productos Más Vendidos
        # st.subheader("Productos Más Vendidos")
        productos_mas_vendidos = df_ventas.groupby('Producto')['Cantidad Vendida'].sum().sort_values(ascending=False)
        fig_productos_mas_vendidos = px.bar(productos_mas_vendidos, x=productos_mas_vendidos.index,
                                            y='Cantidad Vendida', title="Productos Más Vendidos")
        st.plotly_chart(fig_productos_mas_vendidos)
    fig = px.scatter(df_ventas, x='Precio Unitario', y='Cantidad Vendida', title='Relación Precio vs Cantidad Vendida')
    #aplicarFormatoChart(fig)
    st.plotly_chart(fig)
    fig = px.histogram(df_ventas, x='Precio Unitario', title='Distribución de Precios')
    #aplicarFormatoChart(fig)
    st.plotly_chart(fig)

elif selected_tab == 'Copilot Express':
    st.header('Informes-Copilot Work')
    sub_tabs = ['Generación de Tablas', 'Graficas Copilot']
    tabTablas, tabGraficas = st.tabs(sub_tabs)

    with tabGraficas:
        # Definir la ruta donde se guardarán las imágenes
        imagePath = "C:\\Users\\diego\\Escritorio\\WebAPP_Proyect\\images"

        # Asegurarse de que el directorio de imágenes existe, si no, crearlo
        os.makedirs(imagePath, exist_ok=True)

        # Inicializar la lista de imágenes en session_state si no existe
        if 'uploaded_images' not in st.session_state:
            st.session_state.uploaded_images = []

        st.subheader('Graficas Copilot')
        # Mostrar informes estándar para descargar
        uploaded_file = st.file_uploader("Elige una imagen", type=["png", "jpg", "jpeg"])

        if uploaded_file is not None:
            # Leer la imagen usando PIL
            image = Image.open(uploaded_file)

            # Guardar la imagen en la carpeta especificada
            file_path = os.path.join(imagePath, uploaded_file.name)
            image.save(file_path)

            # Agregar el archivo a la lista de imágenes en session_state
            st.session_state.uploaded_images.append(file_path)

            # Mostrar un mensaje de éxito
            st.success(f"Imagen '{uploaded_file.name}' guardada en: {file_path}")

        # Mostrar todas las imágenes cargadas
        st.subheader("Imágenes Cargadas")
        for img_path in st.session_state.uploaded_images:
            image = Image.open(img_path)
            st.image(image, caption=os.path.basename(img_path), use_column_width=True)

    with tabTablas:
        st.subheader('Generación de Tablas')

        # Botón para verificar nuevas hojas
        if st.button('Actualizar tablas'):
            # Inicializar o resetear pagenumber en session_state
            if 'pagenumber' not in st.session_state:
                st.session_state.pagenumber = 3
            else:
                st.session_state.pagenumber = 3

            all_sheets = pd.read_excel(excel_file, sheet_name=None)
            num_sheets = len(all_sheets)

            while st.session_state.pagenumber <= num_sheets:
                sheet_name = list(all_sheets.keys())[st.session_state.pagenumber - 1]

                # Crear la tabla para la hoja actual
                df = pd.read_excel(excel_file, sheet_name=sheet_name)

                # Eliminar filas con valores nulos en la columna especificada
                df.dropna(inplace=True)

                # Mostrar la tabla en Streamlit
                st.write(f"Hoja: {sheet_name}")
                st.dataframe(df)

                st.session_state.pagenumber += 1

elif selected_tab == 'Ayuda y Soporte':
    st.header('Ayuda y Soporte')
    sub_tabs = ['Documentación', 'Preguntas Frecuentes', 'Contacto']
    tabDocu, tabPreguntas, tabContacto = st.tabs(sub_tabs)

    with tabDocu:

        # Mostrar guías y manuales de usuario
        st.markdown("""
        # Documentación del Proyecto

        ## Descripción General
        Esta aplicación permite la gestión de inventarios y ventas, proporcionando herramientas para el análisis de datos y generación de informes.

        ## Funciones Principales

        - **Inicio**: Muestra un resumen de KPIs importantes, gráficos de cantidad vendida por producto y tendencias de ventas mensuales.
        - **Inventario**: Permite ver la tabla de inventario con detalles sobre cada producto y el historial de movimientos de inventario.
        - **Ventas**: Muestra el historial de ventas, gráficos de ventas mensuales y los productos más vendidos.
        - **Copilot Express**: Proporciona opciones para la generación de tablas y gráficos personalizados.
        - **Configuración**: Configuraciones varias y pruebas de gráficos.

        ## Dependencias
        - `pandas`: Para la manipulación de datos.
        - `streamlit`: Para la creación de la interfaz web.
        - `plotly`: Para la generación de gráficos interactivos.
        - `PIL`: Para la manipulación de imágenes.
        - `streamlit_option_menu`: Para la creación de menús de navegación.

        ## Estructura del Proyecto
        - `main.py`: Contiene la lógica principal de la aplicación.
        - `style.css`: Archivo CSS para estilos personalizados.
        - `data/`: Carpeta que contiene los archivos de datos (inventario, ventas, etc.).

        ## Cómo Ejecutar el Proyecto
        1. Clonar el repositorio.
        2. Instalar las dependencias utilizando `pip install -r requirements.txt`.
        3. Ejecutar la aplicación con `streamlit run main.py`.

        ## Funcionalidades Detalladas

        ### Inicio
        - **KPIs**: Muestra indicadores clave como el total de stock, ventas totales y productos con stock bajo.
        - **Gráficos**: Incluye gráficos de cantidad vendida por producto y tendencias de ventas mensuales.

        ### Inventario
        - **Tabla de Inventario**: Visualización detallada del inventario actual.
        - **Historial de Inventario**: Registro de todos los movimientos de inventario.

        ### Ventas
        - **Historial de Ventas**: Detalle de todas las ventas realizadas.
        - **Gráficos de Ventas**: Incluye gráficos de ventas mensuales y productos más vendidos.

        ### Copilot Express
        - **Generación de Tablas**: Genera tablas personalizadas a partir de los datos de ventas e inventario.
        - **Gráficos Copilot**: Muestra gráficos personalizados basados en las imágenes subidas por el usuario.

        ### Configuración
        - **Pruebas de Gráficos**: Sección para probar diferentes visualizaciones de datos.

        ## Contacto
        Para soporte técnico o preguntas, puedes contactarnos a través de [correo@ejemplo.com](mailto:correo@ejemplo.com).

        """)


    with tabPreguntas:
        st.subheader('Preguntas Frecuentes')
        # Mostrar respuestas a preguntas comunes
        faq_items = {
            "¿Cómo puedo agregar un nuevo producto al inventario?": "Para agregar un nuevo producto, dirígete a la sección de Inventario y utiliza el formulario 'Agregar Producto'. Completa los campos requeridos y presiona 'Guardar'.",
            "¿Cómo puedo actualizar la información de un producto existente?": "En la tabla de inventario, selecciona el producto que deseas actualizar y edita los campos necesarios. Luego, presiona 'Guardar Cambios'.",
            "¿Qué sucede si intento vender un producto que está fuera de stock?": "La aplicación notificará que el producto no está disponible y no permitirá registrar la venta hasta que el inventario sea actualizado.",
            "¿Puedo generar reportes de ventas mensuales?": "Sí, en la sección de Ventas puedes seleccionar el período deseado y generar reportes en formato PDF o Excel.",
            "¿Cómo puedo configurar alertas para stock bajo?": "En la sección de Configuración, puedes establecer un umbral de stock bajo para cada producto. La aplicación te notificará cuando un producto esté por debajo de ese nivel.",
            "¿Es posible importar datos de inventario desde un archivo Excel?": "Sí, en la sección de Configuración hay una opción para importar datos desde un archivo Excel. Asegúrate de que el archivo siga el formato especificado.",
            "¿Cómo puedo agregar usuarios y establecer permisos?": "Los usuarios y permisos se pueden gestionar en la sección de Configuración. Puedes agregar nuevos usuarios y asignarles diferentes roles y permisos.",
            "¿La aplicación soporta múltiples idiomas?": "Actualmente, la aplicación está disponible en Español e Inglés. Puedes cambiar el idioma en la sección de Configuración.",
            "¿Qué debo hacer si encuentro un error en la aplicación?": "Si encuentras un error, por favor contáctanos a través de la sección de Contacto o envía un correo a soporte@tuempresa.com.",
            "¿Puedo personalizar el diseño de la aplicación?": "El diseño básico de la aplicación se puede personalizar mediante el archivo `style.css`. Para cambios más avanzados, se necesita acceso al código fuente.",
            "¿La aplicación es compatible con dispositivos móviles?": "Sí, la aplicación es responsive y puede ser utilizada en dispositivos móviles.",
            "¿Cómo puedo respaldar los datos de la aplicación?": "Puedes realizar copias de seguridad de los datos exportando los archivos desde la sección de Configuración.",
            "¿Es posible integrar la aplicación con otros sistemas de gestión?": "Sí, la aplicación ofrece opciones de integración mediante APIs. Para más información, contacta con el equipo de soporte.",
            "¿Hay un límite en el número de productos que puedo agregar?": "No, no hay un límite en el número de productos que puedes agregar a la aplicación.",
            "¿Cómo puedo acceder a las actualizaciones de la aplicación?": "Las actualizaciones se realizan automáticamente. Puedes ver el historial de actualizaciones en la sección de Configuración."
        }

        for question, answer in faq_items.items():
            with st.expander(question):
                st.write(answer)

    with tabContacto:
        st.subheader('Contacto')
        # Formulario de contacto o in""
        contact_form = """
        <form action="https://formsubmit.co/diegopradocam45@gmail.com" method="POST">
            <input type="hidden" name="_captcha" value="false">
            <input type="text" name="name" placeholder="Nombre" required>
            <input type="email" name="email" placeholder="Correo" required>
            <textarea name="message" placeholder="Detalles sobre tu problema"></textarea>
            <button type="submit">Enviar</button>
        </form>
        """

        st.markdown(contact_form, unsafe_allow_html=True)







import streamlit as st
import pandas as pd
import os
from pathlib import Path
import webbrowser
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Avaliador PIM", layout="wide", initial_sidebar_state="expanded")

SUGESTOES_BANCO = {
    "Apresentação Geral": [
        "Faltam diversos elementos obrigatórios conforme normas ABNT",
        "Diagramação inadequada e desorganizada",
        "Linguagem com erros gramaticais e informalidade",
        "Estrutura conforme normas, mas com pequenos ajustes necessários",
        "Excelente apresentação e conformidade com normas"
    ],
    "Introdução": [
        "Falta contexto claro sobre a empresa e o tema",
        "Objetivos não estão explicitamente definidos",
        "Metodologia e estrutura do trabalho não mencionadas",
        "Introdução adequada, mas carece de maior profundidade",
        "Excelente introdução com contexto, objetivos e metodologia bem definidos"
    ],
    "Desenvolvimento": [
        "Abrangência insuficiente das disciplinas propostas",
        "Fraca integração entre teoria e prática",
        "Faltam dados, gráficos e visualizações para suportar análise",
        "Desenvolvimento parcial, com bom conteúdo mas faltam aplicações práticas",
        "Excelente desenvolvimento com integração teórica-prática bem executada"
    ],
    "Discussão": [
        "Sem aplicação das etapas metodológicas indicadas",
        "Ausência de dados e análise crítica do problema",
        "Contextualização superficial das causas do problema",
        "Discussão presente, mas com análise crítica limitada",
        "Excelente discussão com identificação clara do problema e análise profunda"
    ],
    "Conclusão": [
        "Seção não foi desenvolvida",
        "Conclusão genérica sem síntese dos achados",
        "Faltam encaminhamentos concretos e contribuições práticas",
        "Conclusão adequada, mas carece de maior conexão com objetivos",
        "Excelente conclusão com síntese clara e contribuições bem articuladas"
    ],
    "Referências e Citações": [
        "Problemas significativos de padronização e duplicidade",
        "Citações incorretas ou não estão em norma ABNT",
        "Faltam referências ou há excesso de fontes não acadêmicas",
        "Referências adequadas, mas com pequenos problemas de formatação",
        "Excelente padronização das referências e citações conforme ABNT"
    ]
}

DIMENSOES = {
    "Apresentação Geral": 1.0,
    "Introdução": 1.0,
    "Desenvolvimento": 3.0,
    "Discussão": 3.0,
    "Conclusão": 1.0,
    "Referências e Citações": 1.0
}

DIMENSOES_TITULOS = {
    "Apresentação Geral": "APRESENTAÇÃO GERAL DO TRABALHO",
    "Introdução": "INTRODUÇÃO",
    "Desenvolvimento": "DESENVOLVIMENTO",
    "Discussão": "DISCUSSÃO",
    "Conclusão": "CONCLUSÃO",
    "Referências e Citações": "REFERÊNCIAS E CITAÇÕES"
}

RECOMENDACOES_GERAIS = [
    "Revisar estrutura do trabalho conforme normas ABNT",
    "Corrigir erros gramaticais e melhorar clareza da linguagem",
    "Melhorar apresentação do contexto e objetivos do trabalho",
    "Detalhar melhor a metodologia e estrutura adotadas",
    "Aprofundar a integração entre teoria e prática",
    "Incluir mais dados, gráficos e exemplos concretos",
    "Estruturar melhor a análise e discussão do problema",
    "Apresentar mais evidências e dados que sustentem a análise",
    "Elaborar conclusões mais consistentes e bem fundamentadas",
    "Propor encaminhamentos práticos e viáveis",
    "Padronizar todas as referências conforme norma ABNT",
    "Revisar citações e eliminar fontes inadequadas",
    "Melhorar diagramação e formatação visual do documento",
    "Expandir discussão dos resultados encontrados",
    "Incluir mais referências acadêmicas e científicas",
    "Detalhar melhor o problema identificado",
    "Apresentar soluções mais inovadoras e criativas",
    "Melhorar a conexão entre introdução, desenvolvimento e conclusão",
    "Incluir análise crítica mais profunda dos dados",
    "Revisar coesão e coerência do texto",
    "Detalhar melhor a empresa/organização estudada",
    "Integrar melhor as disciplinas do curso no trabalho",
    "Incluir mais informações sobre impacto e resultados",
    "Melhorar apresentação e organização das tabelas e figuras"
]

def calcular_notas(notas_tabela):
    nota_objetiva = sum(notas_tabela.values())
    nota_ponderada = nota_objetiva * 0.70
    return nota_objetiva, nota_ponderada

def gerar_parecer_resumido(dados):
    """
    Gera parecer resumido automático combinando texto padrão com dados da avaliação
    """
    texto_base = (
        "A construção de um trabalho acadêmico envolve variáveis normativas, aspectos formais de pesquisa "
        "e adequação de conteúdos aos tópicos propostos pelo roteiro do Projeto Integrado Multidisciplinar. "
        "Desse modo, a avaliação do PIM (parte escrita) serve ao propósito de contemplar a análise das seguintes "
        "dimensões e critérios de ponderação: cuidados na elaboração da apresentação geral do texto (10%), "
        "introdução (10%), desenvolvimento (30%), discussão—identificação e descrição do problema (30%), "
        "conclusão pertinente aos aspectos estudados (10%) e atenção aos procedimentos de citações e referências (10%). "
        "Para tanto, segue a distribuição dos pontos com o respectivo desempenho discente para cada uma das dimensões avaliadas: "
    )
    
    # Construir detalhes das dimensões
    avaliacoes = dados.get('avaliacoes', {})
    detalhes = []
    
    for dimensao, pesos in DIMENSOES.items():
        avaliacao = avaliacoes.get(dimensao, {})
        nota = avaliacao.get('nota', 0)
        status = avaliacao.get('status', 'Não')
        observacoes = avaliacao.get('observacoes', [])
        comentario = avaliacao.get('comentario', '')
        
        # Montar texto para cada dimensão
        dimensao_texto = f"{dimensao}: Nota {nota:.1f}/{pesos:.1f} ({status})"
        
        # Coletar observações e comentários
        detalhes_obs = []
        if observacoes:
            detalhes_obs.extend(observacoes)
        if comentario:
            detalhes_obs.append(comentario)
        
        # Separar por vírgulas e adicionar ponto final
        if detalhes_obs:
            dimensao_texto += ". " + ", ".join(detalhes_obs) + "."
        else:
            dimensao_texto += "."
        
        detalhes.append(dimensao_texto)
    
    # Calcular nota ponderada da parte escrita
    nota_objetiva = sum(dados.get('notas_tabela', {}).values())
    nota_ponderada_escrita = nota_objetiva * 0.70
    
    # Obter notas da parte oral
    parte_oral = dados.get('parte_oral', 0.0)
    justificativa_oral = dados.get('justificativa_oral', 'Grupo não realizou apresentação')
    
    parecer_completo = texto_base + " ".join(detalhes) + f" Parte Escrita: Nota {nota_ponderada_escrita:.1f}/7.0. Parte Oral: Nota {parte_oral:.1f}/3.0 ({justificativa_oral})."
    return parecer_completo

def gerar_recomendacoes(notas_tabela, avaliacoes):
    recomendacoes = []
    if notas_tabela.get("Apresentação Geral", 0) < 0.7:
        recomendacoes.append("Revisar estrutura do trabalho conforme normas ABNT")
        recomendacoes.append("Corrigir erros gramaticais e melhorar clareza da linguagem")
    if notas_tabela.get("Introdução", 0) < 0.7:
        recomendacoes.append("Melhorar apresentação do contexto e objetivos do trabalho")
        recomendacoes.append("Detalhar melhor a metodologia e estrutura adotadas")
    if notas_tabela.get("Desenvolvimento", 0) < 2.0:
        recomendacoes.append("Aprofundar a integração entre teoria e prática")
        recomendacoes.append("Incluir mais dados, gráficos e exemplos concretos")
    if notas_tabela.get("Discussão", 0) < 2.0:
        recomendacoes.append("Estruturar melhor a análise e discussão do problema")
        recomendacoes.append("Apresentar mais evidências e dados que sustentem a análise")
    if notas_tabela.get("Conclusão", 0) < 0.7:
        recomendacoes.append("Elaborar conclusões mais consistentes e bem fundamentadas")
        recomendacoes.append("Propor encaminhamentos práticos e viáveis")
    if notas_tabela.get("Referências e Citações", 0) < 0.7:
        recomendacoes.append("Padronizar todas as referências conforme norma ABNT")
        recomendacoes.append("Revisar citações e eliminar fontes inadequadas")
    if not recomendacoes:
        recomendacoes.append("Manter a qualidade do trabalho e aprofundar análises quando possível")
    return recomendacoes[:5]

class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado com números de página no rodapé"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._page_num = 0
        self._pages = []

    def showPage(self):
        self._page_num += 1
        self._pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = self._page_num
        for i, page_dict in enumerate(self._pages, 1):
            self.__dict__.update(page_dict)
            self.setFont("Helvetica", 8)
            self.drawString(
                7.5 * inch,
                0.5 * inch,
                f"Página {i} de {total_pages}"
            )
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

def gerar_pdf_relatorio(dados, caminho_saida):
    """
    Gera relatório de avaliação em PDF com paginação correta
    """
    doc = SimpleDocTemplate(
        caminho_saida, 
        pagesize=A4, 
        topMargin=0.5*inch, 
        bottomMargin=1.0*inch,
        leftMargin=0.6*inch, 
        rightMargin=0.6*inch,
        canvasmaker=NumberedCanvas
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=11,
        textColor=colors.HexColor('#000000'),
        spaceAfter=8,
        spaceBefore=0,
        alignment=0,
        bold=True,
        keepWithNext=True
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=4,
        spaceBefore=8,
        bold=True,
        keepWithNext=True
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=8,
        spaceAfter=2,
        leading=10
    )
    
    # Calcular notas
    nota_obj, nota_pond = calcular_notas(dados['notas_tabela'])
    
    # ========== CAPA ==========
    story.append(Paragraph("RELATÓRIO DE AVALIAÇÃO PRELIMINAR DO PIM", titulo_style))
    story.append(Spacer(1, 0.05*inch))
    
    # ========== SEÇÃO I - IDENTIFICAÇÃO ==========
    story.append(Paragraph("I. Identificação", section_style))
    
    ident_text = f"""
    <b>Curso:</b> {dados.get('curso', '')}<br/>
    <b>Turma:</b> {dados.get('turma', '')}<br/>
    <b>PIM:</b> {dados.get('pim', '')}<br/>
    <b>Grupo:</b> {dados.get('grupo', '')}<br/>
    <b>Organização/Empresa:</b> {dados.get('empresa', '')}<br/>
    <b>Professor responsável:</b> {dados.get('professor', '')}<br/>
    <b>Data da avaliação preliminar:</b> {dados.get('data_avaliacao', '')}
    """
    story.append(Paragraph(ident_text, normal_style))
    story.append(Spacer(1, 0.08*inch))
    
    # ========== SEÇÃO II - DIMENSÕES DE AVALIAÇÃO ==========
    story.append(Paragraph("II. Dimensões de Avaliação", section_style))
    story.append(Spacer(1, 0.03*inch))
    
    num_dim = 1
    for chave_dim, titulo_dim_completo in DIMENSOES_TITULOS.items():
        story.append(Paragraph(f"II.{num_dim} {titulo_dim_completo}", section_style))
        
        resposta = dados['avaliacoes'].get(chave_dim, {})
        status = resposta.get('status', 'Não')
        observacoes = resposta.get('observacoes', [])
        comentario = resposta.get('comentario', '')
        
        # Adicionar Status
        story.append(Paragraph(f"<b>Status:</b> {status}", normal_style))
        
        # Mostrar Observações
        if observacoes:
            story.append(Paragraph(f"<b>Observações:</b>", normal_style))
            observacoes_html = '<br/>'.join([f"• {obs}" for obs in observacoes])
            story.append(Paragraph(observacoes_html, normal_style))
        
        # Mostrar Comentários do Professor
        if comentario:
            story.append(Paragraph(f"<b>Comentários do Professor:</b>", normal_style))
            comentario_html = '<br/>'.join([f"• {linha.strip()}" for linha in comentario.split('\n') if linha.strip()])
            story.append(Paragraph(comentario_html, normal_style))
        
        story.append(Spacer(1, 0.04*inch))
        num_dim += 1
    
    # ========== SEÇÃO III - TABELA DE AVALIAÇÃO ==========
    story.append(Paragraph("III. Tabela de Avaliação", section_style))
    
    table_data = [["Dimensão Avaliada", "Nota Máxima", "Nota Atribuída"]]
    
    for dimensao, nota_maxima in DIMENSOES.items():
        resposta = dados['avaliacoes'].get(dimensao, {})
        nota_atribuida = resposta.get('nota', 0)
        dim_tabela = dimensao if "(" not in dimensao else dimensao[:dimensao.index("(")].strip()
        table_data.append([dim_tabela, str(nota_maxima), f"{nota_atribuida:.1f}"])
    
    table_avaliacao = Table(table_data, colWidths=[3.5*inch, 1.0*inch, 1.2*inch])
    table_avaliacao.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d3d3d3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#000000')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(table_avaliacao)
    story.append(Spacer(1, 0.08*inch))
    
    # ========== SEÇÃO IV - RECOMENDAÇÕES GERAIS ==========
    recomendacoes = dados.get('recomendacoes_selecionadas', [])
    comentarios_adicionais = dados.get('comentarios_adicionais', '').strip()
    
    if recomendacoes or comentarios_adicionais:
        story.append(Paragraph("IV. Recomendações Gerais para Aprimoramento", section_style))
        
        if recomendacoes:
            for i, rec in enumerate(recomendacoes, 1):
                story.append(Paragraph(f"• {rec}", normal_style))
        
        if comentarios_adicionais:
            story.append(Spacer(1, 0.03*inch))
            story.append(Paragraph("<b>Notas Adicionais:</b>", normal_style))
            comentarios_formatado = comentarios_adicionais.replace('\n', '<br/>')
            story.append(Paragraph(f"{comentarios_formatado}", normal_style))
        
        story.append(Spacer(1, 0.08*inch))
    
    # ========== SEÇÃO V - CÁLCULO DE NOTAS ==========
    story.append(Paragraph("V. Nota Sugerida", section_style))
    
    notas_resumo = f"""
    <b>Nota Objetiva:</b> {nota_obj:.1f} (nota atribuída considerando o trabalho avaliado em uma escala de 0,0 a 10,0).<br/>
    <b>Nota Ponderada:</b> {nota_pond:.1f} (esta nota considera a avaliação escrita, que corresponde a 70% da nota total do PIM).
    """
    story.append(Paragraph(notas_resumo, normal_style))
    
    # Build PDF
    doc.build(story)

def main():
    st.title("📊 CEOS - Avaliador de Relatórios PIM")
    
    with st.sidebar:
        st.header("📋 Informações do Relatório")
        
        # Listas de opções
        cursos = ["Gestão Financeira", "Gestão RH", "Logística", "Marketing"]
        pims = ["I", "II", "III", "IV"]

        professor = st.text_input("Professor", value="")
        curso = st.selectbox("Curso", cursos, index=0)
        turma = st.text_input("Turma (insira o código)", value="")
        pim = st.selectbox("PIM", pims, index=0)
        grupo = st.text_input("Grupo Nº", value="", max_chars=5)
        empresa = st.text_input("Organização/Empresa", value="")
        data_avaliacao = st.date_input("Data da Avaliação")
        
        st.divider()
        if st.button("🗑️ Zerar Campos", type="secondary", use_container_width=True):
            st.session_state.avaliacoes = {dim: {'status': 'Não', 'nota': 0, 'comentario': '', 'observacoes': []} for dim in DIMENSOES.keys()}
            st.session_state.parecer_final = ""
            st.session_state.notas_tabela = {dim: 0 for dim in DIMENSOES.keys()}
            st.session_state.recomendacoes_selecionadas = []
            st.session_state.comentarios_adicionais = ""
            st.session_state.parte_oral = 0.0
            st.session_state.justificativa_oral = "Grupo não realizou apresentação"
            st.session_state.reset_counter += 1
            
            st.success("✨ Todos os campos foram zerados! Pronto para o próximo grupo.")
            st.balloons()
            import time
            time.sleep(1)
            st.rerun()
        
        st.divider()
    
    tab1, tab_rec, tab2 = st.tabs(["📝 Avaliação", "💡 Recomendações", "📊 Resumo"])
    
    if 'avaliacoes' not in st.session_state:
        st.session_state.avaliacoes = {dim: {'status': 'Não', 'nota': 0, 'comentario': '', 'observacoes': []} for dim in DIMENSOES.keys()}
        st.session_state.notas_tabela = {dim: 0 for dim in DIMENSOES.keys()}
        st.session_state.recomendacoes_selecionadas = []
        st.session_state.parte_oral = 0.0
        st.session_state.justificativa_oral = "Grupo não realizou apresentação"
        st.session_state.reset_counter = 0
    
    with tab1:
        st.header("Avaliação das Dimensões")
        
        for dimensao, nota_maxima in DIMENSOES.items():
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(f"{dimensao} (Nota máxima: {nota_maxima})")
                with col2:
                    status = st.radio(
                        "Status",
                        options=["Sim", "Parcial", "Não"],
                        key=f"status_{dimensao}_{st.session_state.reset_counter}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                    st.session_state.avaliacoes[dimensao]['status'] = status
                
                sugestoes = SUGESTOES_BANCO.get(dimensao, [])
                st.write("**Selecione as sugestões aplicáveis:**")
                
                selecionadas = []
                for i, sugestao in enumerate(sugestoes):
                    if st.checkbox(sugestao, key=f"sug_{dimensao}_{i}_{st.session_state.reset_counter}"):
                        selecionadas.append(sugestao)
                
                comentario_custom = st.text_area(
                    "Ou escreva um comentário customizado",
                    value="",
                    height=60,
                    key=f"comentario_{dimensao}_{st.session_state.reset_counter}",
                    placeholder="Digite aqui comentários adicionais..."
                )
                
                # Salvar separado: observações e comentários do professor
                st.session_state.avaliacoes[dimensao]['observacoes'] = selecionadas
                st.session_state.avaliacoes[dimensao]['comentario'] = comentario_custom
                
                col1, col2 = st.columns(2)
                with col1:
                    nota = st.number_input(
                        f"Nota para {dimensao}",
                        min_value=0.0,
                        max_value=nota_maxima,
                        step=0.1,
                        key=f"nota_{dimensao}_{st.session_state.reset_counter}"
                    )
                    st.session_state.avaliacoes[dimensao]['nota'] = nota
                    st.session_state.notas_tabela[dimensao] = nota
                
                with col2:
                    st.metric("Nota máxima", nota_maxima)
                
                st.divider()
        
        st.subheader("📝 Parecer")
        
        # Calcular nota ponderada da parte escrita
        nota_objetiva = sum(st.session_state.notas_tabela.values())
        nota_ponderada_escrita = nota_objetiva * 0.70
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Parte Escrita (Ponderada)", f"{nota_ponderada_escrita:.1f}/7.0")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            parte_oral = st.number_input(
                "Parte Oral",
                min_value=0.0,
                max_value=3.0,
                step=0.1,
                key=f"parte_oral_{st.session_state.reset_counter}"
            )
            st.session_state.parte_oral = parte_oral
        
        with col2:
            justificativa = st.selectbox(
                "Justificativa",
                ["Grupo não realizou apresentação", "Grupo aguardando para realizar apresentação", "Apresentação realizada"],
                key=f"justificativa_oral_{st.session_state.reset_counter}"
            )
            st.session_state.justificativa_oral = justificativa
        
        st.info("💡 Clique na aba **💡 Recomendações** para instruções adicionais")
    
    with tab_rec:
        st.header("💡 Recomendações Gerais para Aprimoramento")
        st.write("Selecione as recomendações aplicáveis ao trabalho avaliado:")
        
        st.divider()
        
        for i, recomendacao in enumerate(RECOMENDACOES_GERAIS):
            if st.checkbox(recomendacao, key=f"rec_{i}_{st.session_state.reset_counter}"):
                if recomendacao not in st.session_state.recomendacoes_selecionadas:
                    st.session_state.recomendacoes_selecionadas.append(recomendacao)
            else:
                if recomendacao in st.session_state.recomendacoes_selecionadas:
                    st.session_state.recomendacoes_selecionadas.remove(recomendacao)
        
        st.divider()
        st.info(f"💡 {len(st.session_state.recomendacoes_selecionadas)} recomendação(ões) selecionada(s)")
        
        st.divider()
        st.subheader("📝 Comentários Adicionais")
        st.write("Adicione comentários adicionais ou novas sugestões para o grupo:")
        
        comentarios_adicionais = st.text_area(
            "Comentários do Professor",
            value=st.session_state.get('comentarios_adicionais', ''),
            height=150,
            placeholder="Escreva seus comentários, observações ou sugestões adicionais aqui...",
            key=f"comentarios_adicionais_{st.session_state.reset_counter}"
        )
        st.session_state.comentarios_adicionais = comentarios_adicionais
    
    with tab2:
        st.header("📊 Resumo da Avaliação")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Curso", curso)
        with col2:
            st.metric("Turma", turma)
        with col3:
            st.metric("Empresa", empresa if empresa else "N/A")
        with col4:
            st.metric("Data", data_avaliacao.strftime("%d/%m/%Y"))
        
        st.divider()
        
        st.subheader("Notas por Dimensão")
        
        resumo_data = []
        for dimensao, nota_maxima in DIMENSOES.items():
            nota_atribuida = st.session_state.notas_tabela[dimensao]
            status = st.session_state.avaliacoes[dimensao]['status']
            resumo_data.append({
                "Dimensão": dimensao,
                "Nota Máxima": f"{nota_maxima:.1f}",
                "Nota Atribuída": f"{nota_atribuida:.1f}",
                "Status": status
            })
        
        df_resumo = pd.DataFrame(resumo_data)
        
        st.dataframe(df_resumo, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Cálculo de Notas")
        
        nota_obj, nota_pond = calcular_notas(st.session_state.notas_tabela)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Nota Objetiva", f"{nota_obj:.1f}/10.0")
        with col2:
            st.metric("Nota Ponderada (70%)", f"{nota_pond:.2f}")
        with col3:
            st.metric("Fórmula", "Objetiva × 0,70")
        
        st.divider()
        st.subheader("📋 Avaliações Realizadas (Espelho do PDF)")
        
        num_dim = 1
        for chave_dim, titulo_dim_completo in DIMENSOES_TITULOS.items():
            with st.expander(f"{num_dim}. {titulo_dim_completo}"):
                resposta = st.session_state.avaliacoes.get(chave_dim, {})
                status = resposta.get('status', 'Não')
                nota = resposta.get('nota', 0)
                observacoes = resposta.get('observacoes', [])
                comentario = resposta.get('comentario', '')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Status:** {status}")
                with col2:
                    st.write(f"**Nota:** {nota:.1f}/{DIMENSOES[chave_dim]}")
                
                if observacoes:
                    st.write("**Observações:**")
                    for obs in observacoes:
                        st.write(f"• {obs}")
                
                if comentario:
                    st.write("**Comentários do Professor:**")
                    for linha in comentario.split('\n'):
                        if linha.strip():
                            st.write(f"• {linha.strip()}")
                
                if not observacoes and not comentario:
                    st.write("*Sem comentários*")
            
            num_dim += 1
        
        st.divider()
        st.subheader("📝 Parecer Resumido (Automático)")
        
        parecer_resumido = gerar_parecer_resumido({
            'avaliacoes': st.session_state.avaliacoes,
            'notas_tabela': st.session_state.notas_tabela,
            'parte_oral': st.session_state.parte_oral,
            'justificativa_oral': st.session_state.justificativa_oral
        })
        st.info(parecer_resumido)
        
        st.divider()
        if st.button("💾 Gerar PDF", type="primary", use_container_width=True):
            dados_pdf = {
                'curso': curso,
                'turma': turma,
                'pim': pim,
                'grupo': grupo,
                'empresa': empresa,
                'professor': professor,
                'data_avaliacao': data_avaliacao.strftime("%d/%m/%Y"),
                'avaliacoes': st.session_state.avaliacoes,
                'notas_tabela': st.session_state.notas_tabela,
                'recomendacoes_selecionadas': st.session_state.recomendacoes_selecionadas,
                'comentarios_adicionais': st.session_state.get('comentarios_adicionais', ''),
                'parte_oral': st.session_state.parte_oral,
                'justificativa_oral': st.session_state.justificativa_oral
            }
            
            nome_arquivo = f"PIM_{turma}_{empresa.replace(' ', '_')}.pdf"
            
            try:
                # Criar PDF em memória
                pdf_buffer = BytesIO()
                gerar_pdf_relatorio(dados_pdf, pdf_buffer)
                pdf_buffer.seek(0)
                pdf_bytes = pdf_buffer.getvalue()
                
                st.success(f"✅ PDF gerado com sucesso!")
                
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_bytes,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                import traceback
                st.error(traceback.format_exc())


if __name__ == "__main__":
    main()

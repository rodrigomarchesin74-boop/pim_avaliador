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
import json
from datetime import datetime

st.set_page_config(page_title="Avaliador PIM", layout="wide", initial_sidebar_state="expanded")

SUGESTOES_BANCO = {
    "Apresentação Geral": [
        "Seção não apresentada no relatório",
        "A capa não apresenta o nome da instituição, curso, nome dos alunos com RA, título, subtítulo, local e ano de forma clara e organizada",
        "As margens não estão configuradas em 3 cm (esquerda e superior) e 2 cm (direita e inferior)",
        "O espaçamento entre linhas não é de 1,5 cm no corpo do texto",
        "As páginas não estão corretamente numeradas sequencialmente em algarismos arábicos no canto superior direito",
        "O sumário não apresenta todas as seções do relatório em ordem de ocorrência",
        "As tabelas e ilustrações não possuem título, fonte de referência indicada",
        "O texto contém erros ortográficos, de acentuação ou de grafia de palavras",
        "O texto apresenta erros de concordância verbal ou nominal",
        "Estrutura conforme normas, mas com pequenos ajustes necessários",
        "Apresentação adequada e em conformidade com normas"
    ],
    "Introdução": [
        "Seção não apresentada no relatório",
        "A organização escolhida não é apresentada com informações sobre seu ramo de negócio, porte, localização e contexto geral",
        "O relatório não estabelece conexão clara entre o objeto de pesquisa e as disciplinas estudadas no semestre",
        "A introdução não explica por que o PIM é importante para a formação acadêmica dos alunos",
        "O objetivo principal do relatório não está claramente definido",
        "A pesquisa não é justificada quanto à sua importância ou contribuição para a prática profissional",
        "A introdução não descreve a abordagem metodológica utilizada",
        "A introdução não apresenta a estrutura geral do relatório (visão dos capítulos subsequentes)",
        "Introdução adequada com contexto, objetivo e metodologia bem definidos"
    ],
    "Desenvolvimento": [
        "Seção não apresentada no relatório",        
        "Abrangência insuficiente das disciplinas propostas",
        "Fraca integração entre teoria e prática",
        "Faltam dados, gráficos e visualizações para suportar análise",
        "Desenvolvimento parcial, com bom conteúdo mas faltam aplicações práticas",
        "Abordagem prática bem elaborada, porém com conteúdo teórico pouco fundamentado",
        "Desenvolvimento adequado com integração teórica-prática bem executada"
    ],
    "Discussão": {
        "Problema (para PIM I ou PIM II)": [
            "Seção não apresentada no relatório",        
            "O problema principal não está claramente identificado",
            "Os fatores internos e externos que contribuem para o problema não foram descritos",
            "A forma como o problema afeta diferentes áreas da organização não foi demonstrada",
            "As causas-raízes do problema não apresentaram fundamentação adequada",
            "Dados que suportam ou justificam a existência do problema não foram apresentados",
            "Os sintomas não apresentam conexão clara com a realidade observada na organização",
            "As possíveis consequências caso o problema não seja resolvido não foram apresentadas",
            "O problema não está adequadamente relacionado à uma das disciplinas específicas",
            "Discussão adequada, com identificação clara do problema e suas consequências"
        ],
        "Solução (para PIM III ou PIM IV)": [
            "Seção não apresentada no relatório",
            "A solução proposta não está claramente descrita",
            "Os objetivos a serem alcançados com a solução proposta não estão delineados",
            "A solução proposta não está adequadamente justificada",
            "As fases de implementação da solução (cronograma) não foi apresentada",
            "A viabilidade da solução proposta não foi demonstrada",
            "Os benefícios esperados com a implementação da solução não estão claramente descritos",
            "Os indicadores de sucesso - para verificação do alcance da solução - não foram apresentados",
            "Os aspectos que podem limitar a implementação da solução não foram apresentados",
            "A solução não está adequadamente relacionada à uma das disciplinas específicas",
            "A solução proposta está adequadamente fundamentada"
        ]
    },
    "Conclusão": [
        "Seção não apresentada no relatório",
        "Os pontos principais discutidos no desenvolvimento não estão sintetizados",
        "Os desdobramentos da discussão não foram retomados",
        "As limitações encontradas durante a pesquisa não foram mencionadas",
        "A principal contribuição do relatório para a área de estudo ou para a organização não está claramente apresentada",
        "A conclusão não deixa clara a mensagem final que o relatório deseja transmitir",
        "Conclusão adequada, com síntese clara e contribuições bem articuladas"
    ],
    "Referências e Citações": [
        "Seção não apresentada no relatório",
        "Fontes citadas no corpo do texto constam parcialmente na lista de Referências",
        "As Referências não seguem o formato ABNT",
        "Citações diretas apresentaram formatação inconsistente conforme ABNT",
        "Citações indiretas apresentaram formatação inconsistente conforme ABNT",
        "O texto apresenta paráfrases muito próximas de fontes bibliográficas sem a devida atribuição de autoria",
        "Referências adequadas, mas com pequenos problemas de formatação",
        "Padronização adequada das referências e citações, conforme ABNT"
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

def salvar_progresso():
    """Exporta todo o progresso da avaliação em JSON"""
    dados = {
        'versao': '2.1',
        'timestamp': datetime.now().isoformat(),
        'curso': st.session_state.get('curso', ''),
        'lider': st.session_state.get('lider', ''),
        'pim': st.session_state.get('pim', ''),
        'empresa': st.session_state.get('empresa', ''),
        'professor': st.session_state.get('professor', ''),
        'data_avaliacao': st.session_state.get('data_avaliacao', datetime.now()).isoformat(),
        'avaliacoes': st.session_state.get('avaliacoes', {}),
        'notas_tabela': st.session_state.get('notas_tabela', {}),
        'recomendacoes_selecionadas': st.session_state.get('recomendacoes_selecionadas', []),
        'comentarios_adicionais': st.session_state.get('comentarios_adicionais', ''),
        'parte_oral': st.session_state.get('parte_oral', 0.0),
        'justificativa_oral': st.session_state.get('justificativa_oral', ''),
        'tipo_discussao': st.session_state.get('tipo_discussao', 'Problema (PIM I ou II)')
    }
    return json.dumps(dados, indent=2, ensure_ascii=False)

def carregar_progresso(json_data):
    """Restaura progresso salvo do JSON"""
    try:
        dados = json.loads(json_data)
        
        st.session_state.curso = dados.get('curso', '')
        st.session_state.lider = dados.get('lider', '')
        st.session_state.pim = dados.get('pim', '')
        st.session_state.empresa = dados.get('empresa', '')
        st.session_state.professor = dados.get('professor', '')
        
        if 'data_avaliacao' in dados:
            st.session_state.data_avaliacao = datetime.fromisoformat(dados['data_avaliacao'])
        
        st.session_state.avaliacoes = dados.get('avaliacoes', {})
        st.session_state.notas_tabela = dados.get('notas_tabela', {})
        st.session_state.recomendacoes_selecionadas = dados.get('recomendacoes_selecionadas', [])
        st.session_state.comentarios_adicionais = dados.get('comentarios_adicionais', '')
        st.session_state.parte_oral = dados.get('parte_oral', 0.0)
        st.session_state.justificativa_oral = dados.get('justificativa_oral', '')
        st.session_state.tipo_discussao = dados.get('tipo_discussao', 'Problema (PIM I ou II)')
        
        return True, "✅ Avaliação restaurada com sucesso!"
    except Exception as e:
        return False, f"❌ Erro ao carregar: {str(e)}"

def gerar_parecer_resumido(dados):
    """
    Gera parecer resumido automático combinando texto padrão com dados da avaliação
    """
    texto_base = (
        "A construção de um trabalho acadêmico envolve variáveis normativas, aspectos formais de pesquisa "
        "e adequação de conteúdos aos tópicos propostos pelo roteiro do Projeto Integrado Multidisciplinar. "
        "Desse modo, a avaliação do PIM (parte escrita) serve ao propósito de contemplar a análise das seguintes "
        "dimensões e critérios de ponderação: cuidados na elaboração da apresentação geral do texto (10%), "
        "introdução (10%), desenvolvimento (30%), discussão (30%), "
        "conclusão pertinente aos aspectos estudados (10%) e atenção aos procedimentos de citações e referências (10%). "
        "Para tanto, segue a distribuição dos pontos com o respectivo desempenho discente para cada uma das dimensões avaliadas: "
    )
    
    # Construir detalhes das dimensões
    avaliacoes = dados.get('avaliacoes', {})
    detalhes = []
    
    for dimensao, pesos in DIMENSOES.items():
        avaliacao = avaliacoes.get(dimensao, {})
        nota = avaliacao.get('nota', 0)
        observacoes = avaliacao.get('observacoes', [])
        comentario = avaliacao.get('comentario', '')
        
        # Montar texto para cada dimensão
        dimensao_texto = f"{dimensao}: Nota {nota:.1f}/{pesos:.1f}"
        
        # Coletar observações e comentários
        detalhes_obs = []
        if observacoes:
            # Remover tags [Problema] e [Solução]
            for obs in observacoes:
                obs_limpa = obs.replace("[Problema] ", "").replace("[Solução] ", "")
                detalhes_obs.append(obs_limpa)
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
    
    # Calcular nota total
    nota_total = nota_ponderada_escrita + parte_oral
    
    parecer_completo = texto_base + " ".join(detalhes) + f" Parte Escrita: Nota {nota_ponderada_escrita:.1f}/7.0. Parte Oral: Nota {parte_oral:.1f}/3.0 ({justificativa_oral}). Nota Total: {nota_total:.2f}/10.0."
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
    story.append(Paragraph("RELATÓRIO DE AVALIAÇÃO DO PIM", titulo_style))
    story.append(Spacer(1, 0.05*inch))
    
    # ========== SEÇÃO I - IDENTIFICAÇÃO ==========
    story.append(Paragraph("I. Identificação", section_style))
    
    ident_text = f"""
    <b>Curso:</b> {dados.get('curso', '')}<br/>
    <b>PIM:</b> {dados.get('pim', '')}<br/>
    <b>Líder:</b> {dados.get('lider', '')}<br/>
    <b>Organização/Empresa:</b> {dados.get('empresa', '')}<br/>
    <b>Professor responsável:</b> {dados.get('professor', '')}<br/>
    <b>Data da avaliação:</b> {dados.get('data_avaliacao', '')}
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
        observacoes = resposta.get('observacoes', [])
        comentario = resposta.get('comentario', '')
        
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
    
    # ========== SEÇÃO IV - PARECER RESUMIDO ==========
    story.append(Paragraph("IV. Parecer Resumido", section_style))
    
    parecer_dados = {
        'avaliacoes': dados['avaliacoes'],
        'notas_tabela': dados['notas_tabela'],
        'parte_oral': dados['parte_oral'],
        'justificativa_oral': dados['justificativa_oral']
    }
    parecer_texto = gerar_parecer_resumido(parecer_dados)
    story.append(Paragraph(parecer_texto, normal_style))
    story.append(Spacer(1, 0.08*inch))
    
    # ========== SEÇÃO V - NOTAS ATRIBUÍDAS ==========
    story.append(Paragraph("V. Notas Atribuídas", section_style))
    
    # Calcular notas para exibição
    parte_oral = dados.get('parte_oral', 0.0)
    nota_total = nota_pond + parte_oral
    
    notas_resumo = f"""
    <b>Nota Objetiva:</b> {nota_obj:.1f}/10.0 (nota atribuída considerando o trabalho avaliado em uma escala de 0,0 a 10,0).<br/>
    <b>Nota Ponderada (70%):</b> {nota_pond:.2f}/7.0 (esta nota considera a avaliação escrita, que corresponde a 70% da nota total do PIM).<br/>
    <b>Nota Oral:</b> {parte_oral:.1f}/3.0 (nota correspondente à avaliação da apresentação oral, via seminário ou feira acadêmica).<br/>
    <b>Nota Total:</b> {nota_total:.2f}/10.0 (nota efetivamente lançada em sistema acadêmico).
    """
    story.append(Paragraph(notas_resumo, normal_style))
    
    # Build PDF
    doc.build(story)

def main():
    st.title("📊 SATA - Sistema de Avaliação de Trabalho Acadêmico")
    
    with st.sidebar:
        st.header("📋 Informações do Relatório")
        
        # Listas de opções
        cursos = ["Selecionar Curso", "Gestão Financeira", "Gestão RH", "Logística", "Marketing"]
        pims = ["Selecionar PIM", "I", "II", "III", "IV"]

        professor = st.text_input("Professor", value="")
        curso = st.selectbox("Curso", cursos, index=0)
        pim = st.selectbox("PIM", pims, index=0)
        empresa = st.text_input("Organização/Empresa", value="")
        lider = st.text_input("Líder", value="")
        data_avaliacao = st.date_input("Data da Avaliação")
        
        st.divider()
        if st.button("🔄 Nova Correção", type="secondary", use_container_width=True):
            st.session_state.avaliacoes = {dim: {'nota': 0, 'comentario': '', 'observacoes': []} for dim in DIMENSOES.keys()}
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
        
        # ===== PROTEÇÃO DE DADOS =====
        st.markdown("### 💾 Proteção de Dados")
        st.caption("⚠️ O app pode reiniciar e apagar seus dados. Salve periodicamente!")
        
        # Botão de Salvar
        if st.button("⬇️ Salvar Trabalho Atual", use_container_width=True, type="primary"):
            json_backup = salvar_progresso()
            lider = st.session_state.get('lider', 'SemNome').replace(' ', '_')
            empresa = st.session_state.get('empresa', 'SemEmpresa').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            nome_arquivo = f"SATA_{empresa}_{lider}_{timestamp}.json"
            
            st.download_button(
                label="📥 Clique aqui para baixar",
                data=json_backup,
                file_name=nome_arquivo,
                mime="application/json",
                use_container_width=True
            )
        
        # Botão de Carregar
        arquivo_backup = st.file_uploader(
            "⬆️ Continuar Trabalho Salvo",
            type=['json'],
            help="Selecione um arquivo de backup anterior"
        )
        
        if arquivo_backup is not None:
            if st.button("🔄 Restaurar Dados", use_container_width=True):
                conteudo = arquivo_backup.read().decode('utf-8')
                sucesso, mensagem = carregar_progresso(conteudo)
                
                if sucesso:
                    st.success(mensagem)
                    st.balloons()
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(mensagem)
        
        st.divider()
    
    tab_inicio, tab_apresentacao, tab_introducao, tab_desenvolvimento, tab_discussao, tab_conclusao, tab_referencias, tab_parte_oral, tab_relatorio = st.tabs([
        "🏠 Início",
        "📄 Apresentação",
        "📖 Introdução", 
        "📚 Desenvolvimento",
        "💬 Discussão",
        "✅ Conclusão",
        "📚 Referências",
        "🎤 Parte Oral",
        "📋 Relatório"
    ])
    
    if 'avaliacoes' not in st.session_state:
        st.session_state.avaliacoes = {dim: {'nota': 0, 'comentario': '', 'observacoes': []} for dim in DIMENSOES.keys()}
        st.session_state.notas_tabela = {dim: 0 for dim in DIMENSOES.keys()}
        st.session_state.recomendacoes_selecionadas = []
        st.session_state.parte_oral = 0.0
        st.session_state.justificativa_oral = "Grupo não realizou apresentação"
        st.session_state.reset_counter = 0
    
    # ========== ABA INÍCIO ==========
    with tab_inicio:
        st.markdown("""
        ### 👋 Bem-vindo ao SATA!
        
        Este sistema foi desenvolvido para facilitar e padronizar a avaliação do **Projeto Integrado Multidisciplinar (PIM)**.
        
        ---
        
        #### 📋 Como usar:
        
        1. **Preencha os dados na Barra Lateral** (Professor, Curso, PIM, Organização/Empresa, Líder e Data).
        2. **Acesse cada aba** para realizar a avaliação do trabalho.
        3. **Aba Parte Oral** - Registre a nota da apresentação.
        4. **Aba Relatório** - Visualize o resumo completo e gere o PDF.
        
        ---
        
        #### 💡 Dicas Importantes:
        
        - ✅ Use o botão **🔄 Nova Correção** na Barra Lateral para limpar os campos e avaliar outro grupo.
        - 💬 Na aba **Discussão**, escolha entre **Problema (PIM I/II)** ou **Solução (PIM III/IV)** - não é possível preencher ambos.
        - 📄 O **PDF** é gerado automaticamente com todas as informações.
        - 📊 As notas são calculadas automaticamente (Escrita 70% + Oral 30%).
        
        ---
        
        **Dúvidas?** Encaminhe e-mail para rodrigo.marchesin@outlook.com
        """)
    
    # Dicionário com descrições de cada dimensão
    descricoes_dimensoes = {
        "Apresentação Geral": "Conformidade com normas ABNT, diagramação e qualidade da apresentação visual.",
        "Introdução": "Contexto, objetivos e metodologia do trabalho.",
        "Desenvolvimento": "Integração entre teoria e prática, com dados e visualizações das disciplinas correntes no semestre.",
        "Discussão": "Análise e identificação do problema ou da proposição de solução.",
        "Conclusão": "Síntese dos achados e contribuições do trabalho.",
        "Referências e Citações": "Padronização das referências conforme normas ABNT."
    }
    
    # Função para renderizar uma dimensão
    def renderizar_dimensao(tab, dimensao, nota_maxima):
        with tab:
            st.markdown(
                f"<h1 style='color: #1f77b4; font-size: 28px;'>✍️ {dimensao}</h1>",
                unsafe_allow_html=True
            )
            # Adicionar subtítulo explicativo
            st.caption(f"📋 {descricoes_dimensoes.get(dimensao, '')}")
            st.divider()
            
            # Verificar se é Discussão (com grupos Problema/Solução)
            if dimensao == "Discussão" and isinstance(SUGESTOES_BANCO.get(dimensao), dict):
                st.write("**Escolha qual aspecto será abordado:**")
                
                # Radio buttons para escolher entre Problema ou Solução
                tipo_discussao = st.radio(
                    "Tipo de Discussão",
                    options=["Problema (PIM I ou II)", "Solução (PIM III ou IV)"],
                    horizontal=True,
                    key=f"tipo_discussao_{st.session_state.reset_counter}",
                    label_visibility="collapsed"
                )
                
                st.divider()
                st.write("**Selecione as sugestões aplicáveis:**")
                
                selecionadas = []
                
                # Renderizar apenas o grupo escolhido
                if tipo_discussao == "Problema (PIM I ou II)":
                    st.write("🔴 **Problema:**")
                    for i, sugestao in enumerate(SUGESTOES_BANCO[dimensao]["Problema (para PIM I ou PIM II)"]):
                        if st.checkbox(sugestao, key=f"sug_{dimensao}_problema_{i}_{st.session_state.reset_counter}"):
                            selecionadas.append(f"[Problema] {sugestao}")
                else:
                    st.write("🟢 **Solução:**")
                    for i, sugestao in enumerate(SUGESTOES_BANCO[dimensao]["Solução (para PIM III ou PIM IV)"]):
                        if st.checkbox(sugestao, key=f"sug_{dimensao}_solucao_{i}_{st.session_state.reset_counter}"):
                            selecionadas.append(f"[Solução] {sugestao}")
            else:
                # Renderização normal para outras dimensões
                sugestoes = SUGESTOES_BANCO.get(dimensao, [])
                st.write("**Selecione as sugestões aplicáveis:**")
                
                selecionadas = []
                for i, sugestao in enumerate(sugestoes):
                    if st.checkbox(sugestao, key=f"sug_{dimensao}_{i}_{st.session_state.reset_counter}"):
                        selecionadas.append(sugestao)
            
            st.divider()
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
            
            st.divider()
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
    
    # Renderizar cada dimensão em sua aba
    renderizar_dimensao(tab_apresentacao, "Apresentação Geral", DIMENSOES["Apresentação Geral"])
    renderizar_dimensao(tab_introducao, "Introdução", DIMENSOES["Introdução"])
    renderizar_dimensao(tab_desenvolvimento, "Desenvolvimento", DIMENSOES["Desenvolvimento"])
    renderizar_dimensao(tab_discussao, "Discussão", DIMENSOES["Discussão"])
    renderizar_dimensao(tab_conclusao, "Conclusão", DIMENSOES["Conclusão"])
    renderizar_dimensao(tab_referencias, "Referências e Citações", DIMENSOES["Referências e Citações"])
    
    # Aba Parte Oral
    with tab_parte_oral:
        st.markdown(
            "<h1 style='color: #ff6b6b; font-size: 28px;'>🎤 Parte Oral</h1>",
            unsafe_allow_html=True
        )
        
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
    
    # Aba Relatório (com o conteúdo que era antes na aba Resumo)
    with tab_relatorio:
        # Título customizado com cor e ícone diferente
        st.markdown(
            "<h1 style='color: #2ca02c; font-size: 28px;'>📋 Relatório</h1>",
            unsafe_allow_html=True
        )
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Curso", curso)
        with col2:
            st.metric("Líder", lider)
        with col3:
            st.metric("Empresa", empresa if empresa else "N/A")
        with col4:
            st.metric("Data", data_avaliacao.strftime("%d/%m/%Y"))
        
        st.divider()
        
        st.subheader("Notas por Dimensão")
        
        resumo_data = []
        for dimensao, nota_maxima in DIMENSOES.items():
            nota_atribuida = st.session_state.notas_tabela[dimensao]
            resumo_data.append({
                "Dimensão": dimensao,
                "Nota Máxima": f"{nota_maxima:.1f}",
                "Nota Atribuída": f"{nota_atribuida:.1f}"
            })
        
        df_resumo = pd.DataFrame(resumo_data)
        
        st.dataframe(df_resumo, use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("Cálculo de Notas")
        
        nota_obj, nota_pond = calcular_notas(st.session_state.notas_tabela)
        nota_total = nota_pond + st.session_state.parte_oral
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nota Objetiva", f"{nota_obj:.1f}/10.0")
        with col2:
            st.metric("Nota Ponderada (70%)", f"{nota_pond:.2f}/7.0")
        with col3:
            st.metric("Nota Oral", f"{st.session_state.parte_oral:.1f}/3.0")
        with col4:
            st.metric("Nota Total", f"{nota_total:.2f}/10.0", delta=None)
        
        st.divider()
        st.subheader("📋 Avaliações Realizadas (Espelho do PDF)")
        
        num_dim = 1
        for chave_dim, titulo_dim_completo in DIMENSOES_TITULOS.items():
            with st.expander(f"{num_dim}. {titulo_dim_completo}"):
                resposta = st.session_state.avaliacoes.get(chave_dim, {})
                nota = resposta.get('nota', 0)
                observacoes = resposta.get('observacoes', [])
                comentario = resposta.get('comentario', '')
                
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
        st.subheader("📝 Parecer Resumido (texto para ser inserido nos comentários da plataforma do PIM)")
        
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
                'lider': lider,
                'pim': pim,
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
            
            nome_arquivo = f"PIM_{pim}_{empresa.replace(' ', '_')}_{lider.replace(' ', '_')}.pdf"
            
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

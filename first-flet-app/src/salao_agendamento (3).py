import flet as ft
import datetime
import json
import os

class SalaoAgendamento:
    def __init__(self):
        self.agendamentos = []
        self.arquivo_dados = "agendamentos.json"
        self.carregar_agendamentos()
        
        # Serviços disponíveis
        self.servicos = [
            {"nome": "Corte Feminino", "preco": 50.00, "duracao": 60},
            {"nome": "Corte Masculino", "preco": 30.00, "duracao": 45},
            {"nome": "Escova", "preco": 40.00, "duracao": 45},
            {"nome": "Coloração", "preco": 120.00, "duracao": 120},
            {"nome": "Hidratação", "preco": 60.00, "duracao": 60},
            {"nome": "Progressiva", "preco": 200.00, "duracao": 180},
            {"nome": "Manicure", "preco": 25.00, "duracao": 30},
            {"nome": "Pedicure", "preco": 30.00, "duracao": 45}
        ]
        
        # Horários disponíveis
        self.horarios_disponiveis = [
            "  ","08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
            "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
            "17:00", "17:30", "18:00", "18:30"
        ]

    def carregar_agendamentos(self):
        """Carrega agendamentos do arquivo JSON"""
        if os.path.exists(self.arquivo_dados):
            try:
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    self.agendamentos = json.load(f)
            except:
                self.agendamentos = []

    def salvar_agendamentos(self):
        """Salva agendamentos no arquivo JSON"""
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(self.agendamentos, f, ensure_ascii=False, indent=2)

    def verificar_disponibilidade(self, data, horario):
        """Verifica se um horário está disponível"""
        for agendamento in self.agendamentos:
            if agendamento['data'] == data and agendamento['horario'] == horario and agendamento['status'] != 'Removido':
                return False
        return True

    def adicionar_agendamento(self, nome, telefone, servico, data, horario):
        """Adiciona um novo agendamento"""
        servico_info = next((s for s in self.servicos if s['nome'] == servico), None)
        
        agendamento = {
            'id': len(self.agendamentos) + 1,
            'nome': nome,
            'telefone': telefone,
            'servico': servico,
            'preco': servico_info['preco'] if servico_info else 0,
            'duracao': servico_info['duracao'] if servico_info else 60,
            'data': data,
            'horario': horario,
            'status': 'Agendado'
        }
        
        self.agendamentos.append(agendamento)
        self.salvar_agendamentos()
        return True

    def remover_agendamento(self, agendamento_id):
        """Remove um agendamento"""
        for agendamento in self.agendamentos:
            if agendamento['id'] == agendamento_id:
                agendamento['status'] = 'Removido'
                self.salvar_agendamentos()
                return True
        return False

    def marcar_como_concluido(self, agendamento_id):
        """Marca um agendamento como concluído"""
        for agendamento in self.agendamentos:
            if agendamento['id'] == agendamento_id:
                agendamento['status'] = 'Concluído'
                self.salvar_agendamentos()
                return True
        return False

    def obter_agendamentos_ativos(self):
        """Obtém apenas agendamentos ativos (não removidos)"""
        return [a for a in self.agendamentos if a['status'] != 'Removido']

    def obter_agendamentos_do_dia(self, data):
        """Obtém agendamentos de uma data específica (apenas ativos)"""
        return [a for a in self.agendamentos if a['data'] == data and a['status'] != 'Removido']

def main(page: ft.Page):
    page.title = "Salão de Cabeleireiro - Sistema de Agendamento"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 520
    page.window.height = 900  
    page.window.resizable = False
    #trocar cor de fundo
    page.bgcolor = ft.Colors.LIGHT_BLUE_50
    #trocar cor de borda da janela
    page.window.bgcolor = ft.Colors.BLUE_200
    
    # Instância da classe de agendamento
    salao = SalaoAgendamento()
    
    # Componente de mensagem de status
    status_message = ft.Text(
        "",
        size=14,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )
    
    def mostrar_mensagem(texto, cor=ft.Colors.BLUE_600):
        """Exibe uma mensagem de status"""
        status_message.value = texto
        status_message.color = cor
        page.update()
        
        # Remove a mensagem após 3 segundos
        import threading
        def limpar_mensagem():
            import time
            time.sleep(3)
            status_message.value = ""
            page.update()
        
        threading.Thread(target=limpar_mensagem, daemon=True).start()
        
    # Componentes da interface
    nome_field = ft.TextField(
        label="Nome do Cliente",
        width=200,
        border_color=ft.Colors.BLUE_400
    )
    
    telefone_field = ft.TextField(
        label="Telefone",
        width=195,
        border_color=ft.Colors.BLUE_400
    )
    
    servico_dropdown = ft.Dropdown(
        label="Serviço",
        width=200,
        options=[ft.dropdown.Option(s['nome']) for s in salao.servicos],
        border_color=ft.Colors.BLUE_400
    )
    
    data_picker = ft.DatePicker(
        first_date=datetime.datetime.now(),
        last_date=datetime.datetime.now() + datetime.timedelta(days=365)
    )
    
    data_field = ft.TextField(
        label="(DD/MM/AAAA)",
        width=99,
        read_only=False,
        border_color=ft.Colors.BLUE_400
    )
    
    horario_dropdown = ft.Dropdown(
        label="Horário",
        width=145,
        options=[ft.dropdown.Option(h) for h in salao.horarios_disponiveis],
        border_color=ft.Colors.BLUE_400
    )
    
    # Lista de agendamentos
    agendamentos_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.all(10)
    )
    
    def atualizar_lista_agendamentos():
        """Atualiza a lista de agendamentos exibida"""
        agendamentos_list.controls.clear()
        
        # Agrupa agendamentos por data (apenas ativos)
        agendamentos_ativos = salao.obter_agendamentos_ativos()
        agendamentos_por_data = {}
        for agendamento in agendamentos_ativos:
            data = agendamento['data']
            if data not in agendamentos_por_data:
                agendamentos_por_data[data] = []
            agendamentos_por_data[data].append(agendamento)
        
        # Ordena as datas
        for data in sorted(agendamentos_por_data.keys()):
            # Cabeçalho da data
            agendamentos_list.controls.append(

                ft.Container(
                    content=ft.Text(
                        f"📅 {data}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    padding=ft.padding.symmetric(vertical=10)
                )
                
            )
            
            # Agendamentos do dia
            agendamentos_do_dia = sorted(agendamentos_por_data[data], key=lambda x: x['horario'])
            for agendamento in agendamentos_do_dia:
                # Define cor baseada no status
                cor_status = ft.Colors.ORANGE_400 if agendamento['status'] == 'Agendado' else ft.Colors.GREEN_400
                icone_status = "⏰" if agendamento['status'] == 'Agendado' else "✅"
                
                def criar_callback_concluir(agendamento_id):
                    def callback(e):
                        salao.marcar_como_concluido(agendamento_id)
                        atualizar_lista_agendamentos()
                        mostrar_mensagem("Agendamento marcado como concluído!", ft.Colors.GREEN_600)
                    return callback
                
                def criar_callback_remover(agendamento_id):
                    def callback(e):
                        salao.remover_agendamento(agendamento_id)
                        atualizar_lista_agendamentos()
                        mostrar_mensagem("Agendamento removido!", ft.Colors.RED_600)
                    return callback
                
                # Botões de ação
                botoes_acao = []
                if agendamento['status'] == 'Agendado':
                    botoes_acao.extend([
                        ft.IconButton(
                            icon=ft.Icons.CHECK_CIRCLE,
                            tooltip="Marcar como concluído",
                            icon_color=ft.Colors.GREEN_600,
                            on_click=criar_callback_concluir(agendamento['id'])
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Remover agendamento",
                            icon_color=ft.Colors.RED_600,
                            on_click=criar_callback_remover(agendamento['id'])
                        )
                    ])
                elif agendamento['status'] == 'Concluído':
                    botoes_acao.append(
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Remover agendamento",
                            icon_color=ft.Colors.RED_600,
                            on_click=criar_callback_remover(agendamento['id'])
                        )
                    )
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"🕐 {agendamento['horario']}", weight=ft.FontWeight.BOLD),
                                ft.Text(f"👤 {agendamento['nome']}", expand=True),
                                ft.Text(f"💰 R$ {agendamento['preco']:.2f}", color=ft.Colors.GREEN_700),
                                ft.Container(
                                    content=ft.Text(f"{icone_status} {agendamento['status']}", 
                                                   color=ft.Colors.WHITE, size=15),
                                    bgcolor=cor_status,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=10
                                )
                            ]),
                            ft.Row([
                                ft.Text(f"📞 {agendamento['telefone']}"),
                                ft.Text(f"✂️ {agendamento['servico']}", expand=True),
                                ft.Text(f"⏱️ {agendamento['duracao']}min", color=ft.Colors.GREY_700),
                                ft.Row(botoes_acao, spacing=5)
                            ])
                        ]),
                        padding=ft.padding.all(15)
                    ),
                    elevation=2
                )
                agendamentos_list.controls.append(card)
        
        page.update()
    
    def on_date_change(e):
        """Callback para mudança de data"""
        if data_picker.value:
            data_formatada = data_picker.value.strftime("%d/%m/%Y")
            data_field.value = data_formatada
            page.update()
    
    def abrir_date_picker(e):
        """Abre o seletor de data"""
        page.overlay.append(data_picker)
        data_picker.open = True
        page.update()
    
    def agendar_horario(e):
        """Função para agendar um novo horário"""
        # Validações
        if not nome_field.value:
            mostrar_mensagem("Nome é obrigatório!", ft.Colors.RED_600)
            return
        
        if not telefone_field.value or not telefone_field.value.isdigit() or len(telefone_field.value) != 11:
            mostrar_mensagem("Telefone inválido! Informe 11 dígitos numéricos.", ft.Colors.RED_600)
            return
        
        if not servico_dropdown.value:
            mostrar_mensagem("Selecione um serviço!", ft.Colors.RED_600)
            return
        
        if not data_field.value:
            mostrar_mensagem("Selecione uma data!", ft.Colors.RED_600)
            return
        
        if not horario_dropdown.value:
            mostrar_mensagem("Selecione um horário!", ft.Colors.RED_600)
            return
        
        # Verifica disponibilidade
        if not salao.verificar_disponibilidade(data_field.value, horario_dropdown.value):
            mostrar_mensagem("Este horário já está ocupado!", ft.Colors.RED_600)
            return
        
        # Adiciona o agendamento
        sucesso = salao.adicionar_agendamento(
            nome_field.value,
            telefone_field.value,
            servico_dropdown.value,
            data_field.value,
            horario_dropdown.value
        )
        
        if sucesso:
            mostrar_mensagem("Agendamento realizado com sucesso!", ft.Colors.GREEN_600)
            
            # Limpa os campos
            nome_field.value = ""
            telefone_field.value = ""
            servico_dropdown.value = None
            horario_dropdown.value = None
            data_field.value = ""
            
            page.update()
            
            # Atualiza a lista e recarrega a interface
            atualizar_lista_agendamentos()
            
            # Simula uma "reabertura" do aplicativo com uma pequena animação
            page.window.opacity = 0.8
            page.update()
            import time
            time.sleep(0.1)
            page.window.opacity = 1.0
            page.update()
    
    # Configurar callbacks
    data_picker.on_change = on_date_change
    
    # Botões
    btn_data = ft.ElevatedButton(
        "Selecionar Data",
        icon=ft.Icons.CALENDAR_MONTH,
        on_click=abrir_date_picker,
        bgcolor=ft.Colors.BLUE_400,
        color=ft.Colors.WHITE
    )
    
    btn_agendar = ft.ElevatedButton(
        "Agendar Horário",
        icon=ft.Icons.ADD,
        on_click=agendar_horario,
        bgcolor=ft.Colors.GREEN_400,
        color=ft.Colors.WHITE,
        width=200,
        tooltip="Clique para agendar e atualizar a interface"
    )
    
    # Layout principal
    page.add(
        ft.Container(
            content=ft.Column([
                # Cabeçalho
                # Cabeçalho Centralizado
                ft.Container(
                    content=ft.Text(
                        "Salão de Cabeleireiro",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                        # 1. Alinha o texto no centro do espaço do controle Text
                        text_align=ft.TextAlign.CENTER
                    ),
                    bgcolor=ft.Colors.PINK_400,
                    padding=ft.padding.all(20),
                    # 2. Alinha o conteúdo (o Text) no centro do Container
                    alignment=ft.alignment.center,
                    border_radius=10,
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Área de mensagem de status
                ft.Container(
                    content=status_message,
                    height=30,
                    alignment=ft.alignment.center
                ),
                
                # Formulário de agendamento
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Novo Agendamento", size=20,weight=ft.FontWeight.BOLD),
                            ft.Row([nome_field, telefone_field]),
                            ft.Row([servico_dropdown]),
                            ft.Row([data_field, btn_data, horario_dropdown]),
                            ft.Row([btn_agendar], alignment=ft.MainAxisAlignment.CENTER)
                        ]),
                        padding=ft.padding.all(20)
                    ),
                    elevation=5
                ),
                
                # Lista de agendamentos
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📋 Agendamentos", size=20, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(
                                        content=ft.Text("⏰ Agendado", color=ft.Colors.WHITE, size=12),
                                        bgcolor=ft.Colors.ORANGE_400,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=10
                                    ),
                                    ft.Container(
                                        content=ft.Text("✅ Concluído", color=ft.Colors.WHITE, size=12),
                                        bgcolor=ft.Colors.GREEN_400,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        border_radius=10
                                    )
                                ], spacing=10),
                                alignment=ft.alignment.center_right
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Container(
                            content=agendamentos_list,
                            height=300,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                            border_radius=10
                        )
                    ]),
                    margin=ft.margin.only(top=20)
                )
            ]),
            padding=ft.padding.all(20)
        )
    )
    
    # Carrega agendamentos iniciais
    atualizar_lista_agendamentos()

if __name__ == "__main__":
    ft.app(target=main)

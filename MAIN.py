# #---------------------------------------------------------------------------------------


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import random
import re
import json
import os
import math
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime


class MegaSenaApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Mega-Sena | Gerador Avançado")
        self.master.geometry("800x600")
        self.master.configure(bg="#2c3e50")
        
        # Configurações de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#2c3e50')
        self.style.configure('TLabel', background='#2c3e50', foreground='white')
        self.style.configure('TButton', background='#3498db', foreground='white')
        self.style.map('TButton', background=[('active', '#2980b9')])
        self.style.configure('TNotebook', background='#2c3e50', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#34495e', foreground='white')
        self.style.map('TNotebook.Tab', background=[('selected', '#3498db')])
        
        # Variáveis
        self.jogo_atual = []
        self.jogos_gerados = []
        self.historico_jogos = []
        self.estatisticas = Counter()
        self.tema_escuro = True
        
        # Variáveis de exibição
        self.resultado_var = tk.StringVar()
        self.resultado_relatorio = tk.StringVar()
        self.status_var = tk.StringVar(value="Pronto")

        # Variáveis de configuração
        self.config_pares_ou_impares = tk.BooleanVar(value=False)
        self.config_sem_sequencias = tk.BooleanVar(value=False)
        self.quantidade_jogos = tk.IntVar(value=1)
        self.numeros_fixos = tk.StringVar()
        self.numeros_removidos = tk.StringVar()

        # Último concurso simulado
        self.ultimo_concurso = self.gerar_jogo_simulado()
        
        self.criar_interface()
        self.carregar_historico()

    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Aba 1: Gerador
        tab_gerador = ttk.Frame(self.notebook)
        self.notebook.add(tab_gerador, text="Gerador")
        self.criar_aba_gerador(tab_gerador)

        # Aba 2: Relatório
        tab_relatorio = ttk.Frame(self.notebook)
        self.notebook.add(tab_relatorio, text="Relatório")
        self.criar_aba_relatorio(tab_relatorio)

        # Aba 3: Histórico
        tab_historico = ttk.Frame(self.notebook)
        self.notebook.add(tab_historico, text="Histórico")
        self.criar_aba_historico(tab_historico)

        # Aba 4: Estatísticas
        tab_estatisticas = ttk.Frame(self.notebook)
        self.notebook.add(tab_estatisticas, text="Estatísticas")
        self.criar_aba_estatisticas(tab_estatisticas)

        # Barra de status
        status_bar = ttk.Frame(self.master, height=20)
        status_bar.pack(fill="x", side="bottom")
        ttk.Label(status_bar, textvariable=self.status_var).pack(side="left", padx=5)

        # Botão para alternar tema
        ttk.Button(status_bar, text="Alternar Tema", command=self.alternar_tema).pack(side="right", padx=5)

    def criar_aba_gerador(self, parent):
        # Frame esquerdo
        frame_esquerda = ttk.Frame(parent)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Título
        titulo = ttk.Label(
            frame_esquerda,
            text="Gerador de Números da Mega-Sena",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=10)

        # Resultado
        resultado_frame = ttk.Frame(frame_esquerda)
        resultado_frame.pack(fill="x", pady=10)
        
        ttk.Label(resultado_frame, text="Último jogo gerado:", font=("Arial", 10)).pack(anchor="w")
        
        resultado_label = ttk.Label(
            resultado_frame,
            textvariable=self.resultado_var,
            font=("Arial", 24, "bold"),
            foreground="#3498db"
        )
        resultado_label.pack(pady=5)

        # Botões
        botoes_frame = ttk.Frame(frame_esquerda)
        botoes_frame.pack(fill="x", pady=20)
        
        btn_gerar = ttk.Button(
            botoes_frame,
            text="GERAR JOGOS",
            command=self.gerar_numeros,
            width=15
        )
        btn_gerar.pack(side="left", padx=5, pady=5)

        btn_config = ttk.Button(
            botoes_frame,
            text="CONFIGURAÇÕES",
            command=self.abrir_configuracoes,
            width=15
        )
        btn_config.pack(side="left", padx=5, pady=5)

        btn_limpar = ttk.Button(
            botoes_frame,
            text="LIMPAR",
            command=self.limpar_jogos,
            width=15
        )
        btn_limpar.pack(side="left", padx=5, pady=5)

        # Frame direito (histórico recente)
        frame_direita = ttk.Frame(parent)
        frame_direita.pack(side="right", fill="both", padx=10, pady=10)

        ttk.Label(frame_direita, text="Últimos Jogos Gerados", font=("Arial", 12)).pack(pady=5)
        
        self.historico_listbox = tk.Listbox(
            frame_direita, 
            height=10, 
            width=30,
            bg="#34495e",
            fg="white",
            font=("Courier", 10)
        )
        self.historico_listbox.pack(fill="both", expand=True, pady=5)
        
        scrollbar = ttk.Scrollbar(frame_direita, orient="vertical", command=self.historico_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.historico_listbox.config(yscrollcommand=scrollbar.set)
        
        btn_salvar = ttk.Button(
            frame_direita,
            text="SALVAR JOGOS",
            command=self.salvar_jogos
        )
        btn_salvar.pack(pady=5)

    def criar_aba_relatorio(self, parent):
        # Frame principal
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Área de relatório
        ttk.Label(frame, text="Relatório Detalhado", font=("Arial", 14)).pack(pady=5)
        
        self.relatorio_text = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            bg="#34495e",
            fg="white",
            font=("Arial", 10)
        )
        self.relatorio_text.pack(fill="both", expand=True, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame,
            text="Gerar Relatório",
            command=self.gerar_relatorio
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Exportar para TXT",
            command=self.exportar_relatorio
        ).pack(side="left", padx=5)

    def criar_aba_historico(self, parent):
        # Frame principal
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Histórico de Jogos Salvos", font=("Arial", 14)).pack(pady=5)
        
        # Treeview para histórico
        columns = ("#", "Data", "Jogo", "Configurações")
        self.historico_tree = ttk.Treeview(
            frame, 
            columns=columns, 
            show="headings",
            height=15
        )
        
        # Configurar colunas
        for col in columns:
            self.historico_tree.heading(col, text=col)
            self.historico_tree.column(col, width=100, anchor="center")
        
        self.historico_tree.column("#", width=50)
        self.historico_tree.column("Data", width=120)
        self.historico_tree.column("Jogo", width=200)
        
        self.historico_tree.pack(fill="both", expand=True, pady=5)
        
        # Botões
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            btn_frame,
            text="Carregar Histórico",
            command=self.carregar_historico
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Limpar Histórico",
            command=self.limpar_historico
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Excluir Selecionado",
            command=self.excluir_historico
        ).pack(side="right", padx=5)

    def criar_aba_estatisticas(self, parent):
        # Frame principal
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="Estatísticas e Análises", font=("Arial", 14)).pack(pady=5)
        
        # Frame para gráficos
        graph_frame = ttk.Frame(frame)
        graph_frame.pack(fill="both", expand=True, pady=10)
        
        # Gráfico de frequência
        fig, ax = plt.subplots(figsize=(8, 4), facecolor='#2c3e50')
        ax.set_facecolor('#2c3e50')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white')
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')
        
        self.figura = fig
        self.ax = ax
        
        self.canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Frame de controles
        ctrl_frame = ttk.Frame(frame)
        ctrl_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            ctrl_frame,
            text="Atualizar Estatísticas",
            command=self.atualizar_estatisticas
        ).pack(side="left", padx=5)
        
        ttk.Button(
            ctrl_frame,
            text="Exportar Gráfico",
            command=self.exportar_grafico
        ).pack(side="right", padx=5)
        
        # Exibir estatísticas
        self.estatisticas_label = ttk.Label(
            frame,
            text="",
            font=("Arial", 10),
            wraplength=700
        )
        self.estatisticas_label.pack(fill="x", pady=10)
        
        # Inicializar estatísticas
        self.atualizar_estatisticas()

    # 🔢 Função para gerar números
    def gerar_numeros(self):
        self.status_var.set("Gerando jogos...")
        self.master.update()
        
        try:
            self.jogos_gerados = []
            fixos = self.processar_numeros(self.numeros_fixos.get())
            removidos = self.processar_numeros(self.numeros_removidos.get())
            
            # Validar números fixos
            if fixos:
                for num in fixos:
                    if num < 1 or num > 60:
                        messagebox.showerror("Erro", f"Número fixo inválido: {num}\nOs números devem estar entre 1 e 60.")
                        return
                    if num in removidos:
                        messagebox.showerror("Erro", f"Número fixo {num} também está na lista de removidos!")
                        return
                
                if len(fixos) > 6:
                    messagebox.showerror("Erro", "Você não pode ter mais de 6 números fixos!")
                    return
            
            # Validar números removidos
            for num in removidos:
                if num < 1 or num > 60:
                    messagebox.showerror("Erro", f"Número removido inválido: {num}\nOs números devem estar entre 1 e 60.")
                    return

            # Gerar a quantidade solicitada de jogos
            for _ in range(self.quantidade_jogos.get()):
                jogo = self.gerar_um_jogo(fixos, removidos)
                self.jogos_gerados.append(jogo)
                self.atualizar_estatisticas(jogo)
            
            # Atualizar histórico recente
            self.atualizar_historico_recente()
            
            # Exibir o primeiro jogo
            if self.jogos_gerados:
                self.jogo_atual = self.jogos_gerados[0]
                self.resultado_var.set(' - '.join(f"{num:02d}" for num in self.jogo_atual))
                self.status_var.set(f"{len(self.jogos_gerados)} jogos gerados com sucesso!")
        
        except Exception as e:
            self.status_var.set("Erro ao gerar jogos")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    # 🧠 Detecta sequências
    def tem_sequencia(self, numeros):
        numeros = sorted(numeros)
        for i in range(len(numeros) - 2):
            if numeros[i] + 1 == numeros[i + 1] and numeros[i + 1] + 1 == numeros[i + 2]:
                return True
        return False

    # ⚙️ Abrir janela de configurações
    def abrir_configuracoes(self):
        config_win = tk.Toplevel(self.master)
        config_win.title("Configurações")
        config_win.geometry("400x400")
        config_win.configure(bg="#34495e")
        config_win.resizable(False, False)
        config_win.grab_set()

        # Título
        ttk.Label(
            config_win,
            text="⚙️ Configurações de Geração",
            font=("Arial", 14, "bold"),
            background="#34495e",
            foreground="white"
        ).pack(pady=10)

        # Frame para quantidade de jogos
        frame_quantidade = ttk.Frame(config_win)
        frame_quantidade.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(
            frame_quantidade, 
            text="Quantos jogos você quer gerar?",
            background="#34495e",
            foreground="white"
        ).pack(anchor="w")
        
        spin_quant = tk.Spinbox(
            frame_quantidade,
            from_=1,
            to=100,
            textvariable=self.quantidade_jogos,
            width=5,
            bg="#2c3e50",
            fg="white"
        )
        spin_quant.pack(anchor="w", pady=5)

        # Frame para números fixos
        frame_fixos = ttk.Frame(config_win)
        frame_fixos.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(
            frame_fixos, 
            text="Números Fixos (opcional):",
            background="#34495e",
            foreground="white"
        ).pack(anchor="w")
        
        entry_fixos = tk.Entry(
            frame_fixos,
            textvariable=self.numeros_fixos,
            width=30,
            bg="#2c3e50",
            fg="white"
        )
        entry_fixos.pack(fill="x", pady=5)
        ttk.Label(
            frame_fixos, 
            text="(separados por vírgula, espaço, # ou *)",
            font=("Arial", 8),
            background="#34495e",
            foreground="#aaa"
        ).pack(anchor="w")

        # Frame para números removidos
        frame_removidos = ttk.Frame(config_win)
        frame_removidos.pack(fill="x", padx=20, pady=5)
        
        ttk.Label(
            frame_removidos, 
            text="Números Removidos (opcional):",
            background="#34495e",
            foreground="white"
        ).pack(anchor="w")
        
        entry_removidos = tk.Entry(
            frame_removidos,
            textvariable=self.numeros_removidos,
            width=30,
            bg="#2c3e50",
            fg="white"
        )
        entry_removidos.pack(fill="x", pady=5)
        ttk.Label(
            frame_removidos, 
            text="(separados por vírgula, espaço, # ou *)",
            font=("Arial", 8),
            background="#34495e",
            foreground="#aaa"
        ).pack(anchor="w")

        # Checkbuttons
        frame_checks = ttk.Frame(config_win)
        frame_checks.pack(fill="x", padx=20, pady=10)

        chk1 = tk.Checkbutton(
            frame_checks,
            text="Balancear Pares e Ímpares",
            variable=self.config_pares_ou_impares,
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50"
        )
        chk1.pack(anchor="w", pady=3)

        chk2 = tk.Checkbutton(
            frame_checks,
            text="Evitar Sequências (3+ consecutivos)",
            variable=self.config_sem_sequencias,
            bg="#34495e",
            fg="white",
            selectcolor="#2c3e50"
        )
        chk2.pack(anchor="w", pady=3)

        # Botão fechar
        btn_fechar = ttk.Button(
            config_win,
            text="Fechar",
            command=config_win.destroy
        )
        btn_fechar.pack(pady=15)

    # 📊 Gerar relatório detalhado com análises avançadas
    def gerar_relatorio(self):
        if not self.jogos_gerados:
            self.relatorio_text.delete(1.0, tk.END)
            self.relatorio_text.insert(tk.END, "⚠️ Nenhum jogo foi gerado ainda!\nGere jogos primeiro.")
            return
        
        relatorio = "══════════════ RELATÓRIO DE JOGOS ══════════════\n\n"
        relatorio += f"📅 Jogos gerados em: {self.obter_data_hora()}\n"
        relatorio += f"🔢 Total de jogos gerados: {len(self.jogos_gerados)}\n"
        relatorio += f"⚙️ Configurações:\n"
        relatorio += f"   - Pares/Ímpares balanceados: {'Sim' if self.config_pares_ou_impares.get() else 'Não'}\n"
        relatorio += f"   - Evitar sequências: {'Sim' if self.config_sem_sequencias.get() else 'Não'}\n"
        relatorio += f"   - Números fixos: {self.numeros_fixos.get() or 'Nenhum'}\n"
        relatorio += f"   - Números removidos: {self.numeros_removidos.get() or 'Nenhum'}\n\n"
        
        relatorio += "══════════════ DETALHES DOS JOGOS ══════════════\n\n"
        
        for i, jogo in enumerate(self.jogos_gerados, 1):
            relatorio += f"🎯 Jogo {i}: {' - '.join(f'{num:02d}' for num in jogo)}\n"
            
            # Análise avançada do jogo
            analise = self.analisar_jogo(jogo)
            
            relatorio += f"   🔢 Pares: {analise['pares']} | Ímpares: {analise['impares']}\n"
            relatorio += f"   🔍 Primos: {analise['primos']}\n"
            relatorio += f"   🔄 Repetidos (último concurso): {analise['repetidos_ultimo_concurso']}\n"
            relatorio += f"   ➕ Soma: {analise['soma']} | Média: {analise['media']:.2f}\n"
            relatorio += f"   📏 Desvio Padrão: {analise['desvio_padrao']:.2f}\n"
            relatorio += f"   ➗ Múltiplos de 3: {analise['multiplos_3']}\n"
            relatorio += f"   🌀 Números Fibonacci: {analise['fibonacci']}\n"
            relatorio += f"   🔺 Números Triangulares: {analise['triangulares']}\n"
            relatorio += f"   🖼️ Moldura (1-10,51-60): {analise['moldura']} | Centro (11-50): {analise['centro']}\n"
            
            if self.tem_sequencia(jogo):
                relatorio += "   ⚠️ Possui sequência!\n"
            else:
                relatorio += "   ✅ Sem sequência.\n"
                
            relatorio += "\n"
        
        relatorio += "══════════════ ESTATÍSTICAS GERAIS ══════════════\n\n"
        
        # Números mais frequentes
        todos_numeros = [num for jogo in self.jogos_gerados for num in jogo]
        contador = Counter(todos_numeros)
        mais_frequentes = contador.most_common(5)
        
        relatorio += "⭐ Top 5 números mais frequentes:\n"
        for num, count in mais_frequentes:
            relatorio += f"   {num:02d}: {count} vezes\n"
        
        # Distribuição de pares/ímpares
        total_pares = sum(1 for num in todos_numeros if num % 2 == 0)
        total_impares = len(todos_numeros) - total_pares
        
        relatorio += f"\n🔢 Distribuição geral: {total_pares} pares vs {total_impares} ímpares\n"
        
        self.relatorio_text.delete(1.0, tk.END)
        self.relatorio_text.insert(tk.END, relatorio)
        self.status_var.set("Relatório gerado com sucesso!")

    # 🧪 Analisar jogo com métricas avançadas
    def analisar_jogo(self, jogo):
        # Pares e ímpares
        pares = len([n for n in jogo if n % 2 == 0])
        impares = 6 - pares
        
        # Números primos
        primos = len([n for n in jogo if self.eh_primo(n)])
        
        # Repetidos do último concurso
        repetidos = len(set(jogo) & set(self.ultimo_concurso))
        
        # Soma e média
        soma = sum(jogo)
        media = soma / 6
        
        # Desvio padrão
        variancia = sum((x - media) ** 2 for x in jogo) / 6
        desvio_padrao = math.sqrt(variancia)
        
        # Múltiplos de 3
        multiplos_3 = len([n for n in jogo if n % 3 == 0])
        
        # Fibonacci
        fibonacci = len([n for n in jogo if self.eh_fibonacci(n)])
        
        # Triangulares
        triangulares = len([n for n in jogo if self.eh_triangular(n)])
        
        # Moldura e centro
        moldura = len([n for n in jogo if n <= 10 or n >= 51])
        centro = 6 - moldura
        
        return {
            'pares': pares,
            'impares': impares,
            'primos': primos,
            'repetidos_ultimo_concurso': repetidos,
            'soma': soma,
            'media': media,
            'desvio_padrao': desvio_padrao,
            'multiplos_3': multiplos_3,
            'fibonacci': fibonacci,
            'triangulares': triangulares,
            'moldura': moldura,
            'centro': centro
        }
    
    # 🧮 Funções auxiliares para análise
    
    def eh_primo(self, n):
        """Verifica se um número é primo"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def eh_fibonacci(self, n):
        """Verifica se um número pertence à sequência de Fibonacci"""
        # Um número é Fibonacci se e somente se (5*n² + 4) ou (5*n² - 4) é um quadrado perfeito
        x = 5 * n * n
        return math.isqrt(x + 4) ** 2 == x + 4 or math.isqrt(x - 4) ** 2 == x - 4
    
    def eh_triangular(self, n):
        """Verifica se um número é triangular"""
        # Resolve a equação n = k(k+1)/2
        # k = (sqrt(8n+1) - 1)/2
        k = (math.sqrt(8 * n + 1) - 1) / 2
        return k.is_integer()
    
    def gerar_jogo_simulado(self):
        """Gera um jogo aleatório para simular o último concurso"""
        return sorted(random.sample(range(1, 61), 6))

    # 🛠️ Processar números digitados pelo usuário
    def processar_numeros(self, entrada):
        if not entrada.strip():
            return []
        
        entrada = re.sub(r'[,#*]', ' ', entrada)
        try:
            return [int(num) for num in entrada.split()]
        except ValueError:
            messagebox.showerror("Erro", "Formato inválido para números!\nUse apenas números separados por espaços ou vírgulas.")
            return []

    # 🎲 Gerar um único jogo
    def gerar_um_jogo(self, fixos, removidos):
        numeros = fixos[:]
        disponiveis = [num for num in range(1, 61) 
                       if num not in fixos and num not in removidos]
        
        faltam = 6 - len(numeros)
        
        tentativas = 0
        while True:
            tentativas += 1
            if tentativas > 1000:
                break
                
            complemento = random.sample(disponiveis, faltam)
            jogo = sorted(numeros + complemento)
            
            if self.config_pares_ou_impares.get():
                pares = len([n for n in jogo if n % 2 == 0])
                impares = 6 - pares
                if abs(pares - impares) > 2:
                    continue
                    
            if self.config_sem_sequencias.get():
                if self.tem_sequencia(jogo):
                    continue
                    
            break
            
        return jogo

    # 💾 Salvar jogos gerados
    def salvar_jogos(self):
        if not self.jogos_gerados:
            messagebox.showinfo("Informação", "Nenhum jogo para salvar!")
            return
        
        try:
            # Criar registro
            registro = {
                "data": self.obter_data_hora(),
                "jogos": self.jogos_gerados,
                "config": {
                    "pares_impares": self.config_pares_ou_impares.get(),
                    "sem_sequencias": self.config_sem_sequencias.get(),
                    "fixos": self.numeros_fixos.get(),
                    "removidos": self.numeros_removidos.get()
                }
            }
            
            # Adicionar ao histórico
            self.historico_jogos.append(registro)
            
            # Salvar em arquivo
            with open("historico_mega_sena.json", "w") as f:
                json.dump(self.historico_jogos, f, indent=2)
            
            # Atualizar histórico
            self.carregar_historico()
            self.status_var.set(f"{len(self.jogos_gerados)} jogos salvos no histórico!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar jogos: {str(e)}")

    # 📂 Carregar histórico
    def carregar_historico(self):
        try:
            if os.path.exists("historico_mega_sena.json"):
                with open("historico_mega_sena.json", "r") as f:
                    self.historico_jogos = json.load(f)
            
            # Atualizar Treeview
            self.historico_tree.delete(*self.historico_tree.get_children())
            
            for i, registro in enumerate(self.historico_jogos, 1):
                jogos_str = ", ".join(["-".join(map(str, jogo)) for jogo in registro["jogos"]])
                config_str = f"Pares: {registro['config']['pares_impares']}, Seq: {registro['config']['sem_sequencias']}"
                
                self.historico_tree.insert("", "end", values=(
                    i,
                    registro["data"],
                    jogos_str[:50] + "..." if len(jogos_str) > 50 else jogos_str,
                    config_str
                ))
            
            self.status_var.set(f"Histórico carregado: {len(self.historico_jogos)} registros")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar histórico: {str(e)}")

    # 📊 Atualizar estatísticas
    def atualizar_estatisticas(self, novo_jogo=None):
        # Atualizar contagem
        if novo_jogo:
            for num in novo_jogo:
                self.estatisticas[num] += 1
        
        # Gerar texto de estatísticas
        if self.estatisticas:
            total_jogos = sum(self.estatisticas.values()) / 6
            estat_texto = f"📊 Estatísticas baseadas em {total_jogos:.0f} jogos:\n"
            estat_texto += f"⭐ Número mais frequente: {self.estatisticas.most_common(1)[0][0]} ({self.estatisticas.most_common(1)[0][1]} vezes)\n"
            estat_texto += f"👎 Número menos frequente: {self.estatisticas.most_common()[-1][0]} ({self.estatisticas.most_common()[-1][1]} vezes)\n"
            
            # Top 5 números mais sorteados
            estat_texto += "\n🏆 Top 5 números mais sorteados:\n"
            for num, count in self.estatisticas.most_common(5):
                estat_texto += f"   {num:02d}: {count} vezes ({count/total_jogos:.1%})\n"
        else:
            estat_texto = "Nenhum dado estatístico disponível.\nGere alguns jogos primeiro."
        
        self.estatisticas_label.config(text=estat_texto)
        
        # Atualizar gráfico
        self.atualizar_grafico()

    # 📈 Atualizar gráfico de frequência
    def atualizar_grafico(self):
        self.ax.clear()
        
        if not self.estatisticas:
            self.ax.text(0.5, 0.5, 'Sem dados', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=15, color='white')
            self.canvas.draw()
            return
        
        # Preparar dados
        numeros = list(range(1, 61))
        frequencias = [self.estatisticas.get(num, 0) for num in numeros]
        
        # Criar gráfico
        self.ax.bar(numeros, frequencias, color='#3498db')
        self.ax.set_title('Frequência de Números', color='white')
        self.ax.set_xlabel('Números', color='white')
        self.ax.set_ylabel('Frequência', color='white')
        self.ax.set_xticks(range(1, 61, 5))
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        self.canvas.draw()

    # 🔄 Atualizar histórico recente
    def atualizar_historico_recente(self):
        self.historico_listbox.delete(0, tk.END)
        
        for i, jogo in enumerate(self.jogos_gerados, 1):
            jogo_str = f"{i:02d}. {' - '.join(f'{num:02d}' for num in jogo)}"
            self.historico_listbox.insert(tk.END, jogo_str)

    # 🗑️ Limpar jogos atuais
    def limpar_jogos(self):
        self.jogos_gerados = []
        self.resultado_var.set("")
        self.historico_listbox.delete(0, tk.END)
        self.relatorio_text.delete(1.0, tk.END)
        self.status_var.set("Jogos limpos")

    # 🗑️ Limpar histórico completo
    def limpar_historico(self):
        if messagebox.askyesno("Confirmar", "Tem certeza que deseja limpar todo o histórico?"):
            self.historico_jogos = []
            self.historico_tree.delete(*self.historico_tree.get_children())
            
            try:
                if os.path.exists("historico_mega_sena.json"):
                    os.remove("historico_mega_sena.json")
                self.status_var.set("Histórico limpo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao limpar histórico: {str(e)}")

    # 🗑️ Excluir item do histórico
    def excluir_historico(self):
        selecionado = self.historico_tree.selection()
        if not selecionado:
            messagebox.showinfo("Informação", "Nenhum item selecionado!")
            return

        if messagebox.askyesno("Confirmar", "Excluir o registro selecionado?"):
            item = selecionado[0]
            valores = self.historico_tree.item(item, 'values')

            # Supondo que o primeiro valor é a posição do item na lista:
            try:
                idx = int(valores[0]) - 1  # Se você estiver mostrando um índice na primeira coluna
            except (IndexError, ValueError):
                messagebox.showerror("Erro", "Erro ao obter o índice do item selecionado.")
                return

            # Verificar se o índice existe na lista
            if 0 <= idx < len(self.historico_jogos):
                del self.historico_jogos[idx]

                # Salvar alterações
                with open("historico_mega_sena.json", "w") as f:
                    json.dump(self.historico_jogos, f, indent=2)

                # Recarregar histórico
                self.carregar_historico()
                self.status_var.set("Registro excluído com sucesso!")
            else:
                messagebox.showerror("Erro", "Índice fora dos limites do histórico.")


    # 💾 Exportar relatório para arquivo
    def exportar_relatorio(self):
        if not self.jogos_gerados:
            messagebox.showinfo("Informação", "Nenhum relatório para exportar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, "w") as f:
                f.write(self.relatorio_text.get(1.0, tk.END))
            self.status_var.set(f"Relatório exportado para: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar relatório: {str(e)}")

    # 📤 Exportar gráfico
    def exportar_grafico(self):
        if not self.estatisticas:
            messagebox.showinfo("Informação", "Nenhum dado estatístico disponível!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg"), ("Todos os arquivos", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.figura.savefig(file_path, dpi=300, facecolor='#2c3e50')
            self.status_var.set(f"Gráfico exportado para: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar gráfico: {str(e)}")

    # 🌗 Alternar entre tema claro e escuro
    def alternar_tema(self):
        self.tema_escuro = not self.tema_escuro
        
        if self.tema_escuro:
            # Tema escuro
            bg_color = "#2c3e50"
            fg_color = "white"
            widget_bg = "#34495e"
        else:
            # Tema claro
            bg_color = "#f0f0f0"
            fg_color = "black"
            widget_bg = "white"
        
        # Atualizar cores principais
        self.master.configure(bg=bg_color)
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TNotebook', background=bg_color)
        self.style.configure('TNotebook.Tab', background=widget_bg, foreground=fg_color)
        
        # Atualizar widgets específicos
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Listbox) or isinstance(widget, scrolledtext.ScrolledText):
                widget.configure(bg=widget_bg, fg=fg_color)
        
        # Atualizar gráfico
        self.atualizar_grafico()

    # ⏱️ Obter data e hora formatada
    def obter_data_hora(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


if __name__ == "__main__":
    root = tk.Tk()
    app = MegaSenaApp(root)
    root.mainloop()
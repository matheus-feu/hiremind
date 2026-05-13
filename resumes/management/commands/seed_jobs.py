"""Popula o banco com vagas de exemplo usando Faker pt_BR."""
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from resumes.models import Job


class JobGenerator:
	"""Gerador de vagas realistas usando Faker pt_BR."""

	def __init__(self):
		self.fake = Faker("pt_BR")
		Faker.seed(42)  # Seed para reprodutibilidade

		# Configuração de áreas e stacks
		self.areas = {
			"backend": {
				"stacks": {
					"Python": {
						"frameworks": ["Django", "FastAPI", "Flask", "DRF", "SQLAlchemy", "Celery"],
						"skills": ["REST APIs", "PostgreSQL", "Redis", "Docker", "Git"],
						"optional": ["GraphQL", "MongoDB", "AWS", "Kubernetes", "RabbitMQ", "pytest"],
					},
					"Java": {
						"frameworks": ["Spring Boot", "Hibernate", "JPA", "Maven", "Gradle"],
						"skills": ["REST APIs", "PostgreSQL", "MySQL", "Git", "Docker"],
						"optional": ["Microservices", "Kafka", "AWS", "Jenkins", "Kubernetes"],
					},
					"Node.js": {
						"frameworks": ["NestJS", "Express", "TypeScript", "Prisma", "Sequelize"],
						"skills": ["JavaScript", "REST APIs", "MongoDB", "PostgreSQL", "Git"],
						"optional": ["GraphQL", "Redis", "AWS", "Docker", "Microservices"],
					},
					"Go": {
						"frameworks": ["Gin", "Echo", "GORM", "Fiber"],
						"skills": ["REST APIs", "PostgreSQL", "Redis", "Docker", "Git"],
						"optional": ["gRPC", "Kubernetes", "Microservices", "AWS", "Protocol Buffers"],
					},
				},
				"responsibilities": [
					"Desenvolver e manter APIs RESTful de alta performance",
					"Participar do design de arquitetura de sistemas escaláveis",
					"Realizar code reviews e pair programming",
					"Escrever testes automatizados (unitários e integração)",
					"Otimizar queries e performance do banco de dados",
					"Documentar APIs e processos técnicos",
					"Colaborar com times de frontend e mobile",
					"Implementar best practices de segurança",
				],
			},
			"frontend": {
				"stacks": {
					"React": {
						"frameworks": ["Redux", "React Query", "Styled Components", "Material-UI", "Vite"],
						"skills": ["JavaScript", "TypeScript", "HTML", "CSS", "Git"],
						"optional": ["Next.js", "Jest", "Cypress", "Storybook", "Tailwind CSS", "Webpack"],
					},
					"Vue.js": {
						"frameworks": ["Vuex", "Pinia", "Nuxt.js", "Vuetify", "Vite"],
						"skills": ["JavaScript", "TypeScript", "HTML", "CSS", "Git"],
						"optional": ["Jest", "Cypress", "Tailwind CSS", "Storybook", "Vitest"],
					},
					"Angular": {
						"frameworks": ["RxJS", "NgRx", "Angular Material", "TypeScript"],
						"skills": ["TypeScript", "HTML", "CSS", "Git", "REST APIs"],
						"optional": ["Jest", "Jasmine", "Karma", "Protractor", "SCSS"],
					},
				},
				"responsibilities": [
					"Desenvolver interfaces web modernas e responsivas",
					"Implementar componentes reutilizáveis e acessíveis",
					"Integrar com APIs REST/GraphQL",
					"Garantir acessibilidade (WCAG 2.1)",
					"Otimizar performance e Core Web Vitals",
					"Trabalhar próximo ao time de UX/UI Design",
					"Escrever testes de componentes e E2E",
					"Implementar versionamento semântico",
				],
			},
			"mobile": {
				"stacks": {
					"React Native": {
						"frameworks": ["Expo", "Redux", "React Navigation", "TypeScript", "Reanimated"],
						"skills": ["JavaScript", "React", "Git", "REST APIs", "Mobile UI/UX"],
						"optional": ["Firebase", "Push Notifications", "Deep Linking", "CodePush"],
					},
					"Flutter": {
						"frameworks": ["Dart", "BLoC", "Provider", "Riverpod", "GetX"],
						"skills": ["Dart", "Git", "REST APIs", "Material Design", "iOS/Android"],
						"optional": ["Firebase", "SQLite", "GraphQL", "Hive", "Freezed"],
					},
				},
				"responsibilities": [
					"Desenvolver aplicativos mobile nativos",
					"Implementar designs responsivos e animações",
					"Integrar com APIs backend e serviços externos",
					"Publicar e gerenciar apps nas lojas (App Store/Play Store)",
					"Otimizar performance e consumo de bateria",
					"Implementar analytics, crash reporting e feature flags",
					"Garantir compatibilidade entre versões de OS",
				],
			},
			"fullstack": {
				"stacks": {
					"MERN": {
						"frameworks": ["MongoDB", "Express", "React", "Node.js", "TypeScript"],
						"skills": ["JavaScript", "REST APIs", "Git", "Docker", "NoSQL"],
						"optional": ["GraphQL", "Redis", "AWS", "Next.js", "Mongoose"],
					},
					"Django + React": {
						"frameworks": ["Django", "DRF", "React", "PostgreSQL", "TypeScript"],
						"skills": ["Python", "JavaScript", "REST APIs", "Git", "Docker"],
						"optional": ["TypeScript", "Redux", "Celery", "AWS", "Next.js"],
					},
				},
				"responsibilities": [
					"Desenvolver features end-to-end (frontend + backend)",
					"Criar e integrar APIs RESTful",
					"Implementar interfaces de usuário modernas",
					"Gerenciar banco de dados e migrações",
					"Deploy e manutenção de aplicações em produção",
					"Garantir qualidade através de testes",
				],
			},
			"data": {
				"stacks": {
					"Python Data": {
						"frameworks": ["Pandas", "PySpark", "Airflow", "dbt", "SQL"],
						"skills": ["Python", "SQL", "ETL", "Data Modeling", "Git"],
						"optional": ["Snowflake", "BigQuery", "AWS", "Databricks", "Kafka", "Terraform"],
					},
				},
				"responsibilities": [
					"Construir e manter pipelines de dados (ETL/ELT)",
					"Modelar data warehouses e data lakes",
					"Otimizar queries e performance de processos",
					"Criar dashboards e relatórios analíticos",
					"Garantir qualidade e governança dos dados",
					"Implementar monitoramento de pipelines",
				],
			},
			"devops": {
				"stacks": {
					"DevOps/SRE": {
						"frameworks": ["Docker", "Kubernetes", "Terraform", "Ansible", "Helm"],
						"skills": ["Linux", "CI/CD", "AWS", "Git", "Bash/Python"],
						"optional": ["Prometheus", "Grafana", "Jenkins", "ArgoCD", "Datadog", "GitHub Actions"],
					},
				},
				"responsibilities": [
					"Gerenciar infraestrutura cloud (AWS/Azure/GCP)",
					"Implementar e manter pipelines CI/CD",
					"Configurar monitoramento, logging e alertas",
					"Automatizar processos de deploy e rollback",
					"Garantir segurança e compliance (SOC2, ISO 27001)",
					"Participar de incident response e post-mortems",
					"Otimizar custos de infraestrutura",
				],
			},
			"ml": {
				"stacks": {
					"Machine Learning": {
						"frameworks": ["PyTorch", "TensorFlow", "scikit-learn", "Pandas", "NumPy"],
						"skills": ["Python", "Statistics", "ML Algorithms", "Git", "MLOps"],
						"optional": ["LangChain", "Hugging Face", "MLflow", "Kubernetes", "AWS SageMaker", "Vector DBs"],
					},
				},
				"responsibilities": [
					"Desenvolver e treinar modelos de machine learning",
					"Realizar análise exploratória e feature engineering",
					"Deploy de modelos em produção (MLOps)",
					"Monitorar performance e drift de modelos",
					"Trabalhar com LLMs, RAG e fine-tuning",
					"Otimizar modelos para produção",
				],
			},
		}

		# Níveis de senioridade
		self.seniorities = [
			("Júnior", Job.SeniorityChoices.JUNIOR, 0),
			("Pleno", Job.SeniorityChoices.MID_LEVEL, 3),
			("Sênior", Job.SeniorityChoices.SENIOR, 5),
			("Especialista", Job.SeniorityChoices.SPECIALIST, 8),
		]

		# Departamentos
		self.departments = [
			"Tecnologia", "Engenharia de Software", "Produto", "Inovação",
			"Data & Analytics", "Plataforma", "Infraestrutura", "Mobile", "Cloud"
		]

		# Benefícios
		self.all_benefits = [
			"Vale refeição/alimentação (R$ 30/dia)",
			"Plano de saúde (coparticipativo)",
			"Plano de saúde sem coparticipação",
			"Plano odontológico",
			"Vale transporte ou estacionamento",
			"Auxílio home office (R$ 200/mês)",
			"Auxílio educação/cursos (até R$ 500/mês)",
			"Gympass/Totalpass",
			"Day off de aniversário",
			"Horário flexível (flex time)",
			"Licença maternidade/paternidade estendida",
			"Seguro de vida",
			"Participação nos lucros (PLR)",
			"Stock options/RSU",
			"Budget para equipamentos (R$ 3.000)",
			"Convênio com universidades",
			"Programa de mentoria",
			"Wellhub (antigo Gympass)",
		]

	def generate_job(self):
		"""Gera uma vaga completa com dados faker pt_BR."""
		# Escolhe área e stack
		area = random.choice(list(self.areas.keys()))
		stack_name = random.choice(list(self.areas[area]["stacks"].keys()))
		stack_data = self.areas[area]["stacks"][stack_name]

		# Escolhe senioridade
		level_name, seniority, min_exp = random.choice(self.seniorities)

		# Gera dados da empresa (usando Faker pt_BR)
		company = self.fake.company()

		# Gera título
		title = self._generate_title(area, stack_name, level_name)

		# Gera descrição contextualizada
		description = self._generate_description(area, level_name, company)

		# Gera skills
		required_skills, nice_to_have = self._generate_skills(stack_name, stack_data)

		# Localização e modelo de trabalho
		work_model = random.choice(list(Job.WorkModelChoices))
		location = self.fake.city() if work_model != Job.WorkModelChoices.REMOTE else "Remoto - Brasil"

		# Tipo de contrato
		contract_type = random.choices([
			Job.ContractTypeChoices.CLT,
			Job.ContractTypeChoices.PJ,
		], weights=[70, 30])[0]

		# Salário baseado em senioridade
		salary_min, salary_max = self._generate_salary(seniority, contract_type)

		# Benefícios
		benefits = self._generate_benefits()

		# Outros campos
		department = random.choice(self.departments)
		openings = random.choices([1, 2, 3, 5], weights=[70, 20, 7, 3])[0]

		# Prazo de candidatura (30-90 dias)
		deadline = timezone.now().date() + timedelta(days=random.randint(30, 90))

		return {
			"title": title,
			"seniority": seniority,
			"description": description,
			"required_skills": required_skills,
			"nice_to_have": nice_to_have,
			"min_experience_years": min_exp + random.choice([0, 0.5, 1]),
			"location": location,
			"work_model": work_model,
			"contract_type": contract_type,
			"salary_min": salary_min,
			"salary_max": salary_max,
			"salary_visible": random.choices([True, False], weights=[30, 70])[0],
			"benefits": benefits,
			"department": department,
			"openings": openings,
			"application_deadline": deadline,
			"education_level": random.choice([
				Job.EducatinonLevelChoices.NONE,
				Job.EducatinonLevelChoices.BACHELORS,
				Job.EducatinonLevelChoices.ASSOCIATE,
			]),
			"languages": random.choice(["", "Inglês intermediário", "Inglês avançado"]),
			"is_active": True,
		}

	def _generate_title(self, area, stack, level):
		"""Gera título da vaga."""
		templates = {
			"backend": [
				f"Desenvolvedor(a) Backend {stack} - {level}",
				f"Backend Developer {stack} | {level}",
				f"Engenheiro(a) de Software Backend ({stack}) - {level}",
			],
			"frontend": [
				f"Desenvolvedor(a) Frontend {stack} - {level}",
				f"Frontend Developer {level}",
				f"Engenheiro(a) Frontend {stack} | {level}",
			],
			"mobile": [
				f"Desenvolvedor(a) Mobile {stack} - {level}",
				f"Mobile Developer ({stack}) | {level}",
			],
			"fullstack": [
				f"Desenvolvedor(a) Full-Stack - {level}",
				f"Full-Stack Developer ({stack}) - {level}",
				f"Engenheiro(a) Full-Stack | {level}",
			],
			"data": [
				f"Engenheiro(a) de Dados - {level}",
				f"Data Engineer | {level}",
				f"Analista de Dados - {level}",
			],
			"devops": [
				f"DevOps Engineer - {level}",
				f"SRE (Site Reliability Engineer) | {level}",
				f"Engenheiro(a) de Infraestrutura Cloud - {level}",
			],
			"ml": [
				f"Engenheiro(a) de Machine Learning - {level}",
				f"ML Engineer | {level}",
				f"Cientista de Dados - {level}",
			],
		}
		return random.choice(templates.get(area, [f"Desenvolvedor(a) {level}"]))

	def _generate_description(self, area, level, company):
		"""Gera descrição realista usando Faker."""
		intros = [
			f"A {company} está em busca de profissional {level} para integrar nosso time de tecnologia em constante crescimento.",
			f"Junte-se à {company}! Procuramos {level} apaixonado(a) por tecnologia e inovação.",
			f"Venha fazer parte da transformação digital na {company}. Buscamos {level} para nosso time.",
			f"A {company} cresce e precisa de você! Oportunidade para {level} que deseja fazer a diferença.",
		]

		intro = random.choice(intros)

		# Adiciona um contexto sobre a empresa
		contexts = [
			f"\n\nSomos uma {random.choice(['startup', 'scale-up', 'empresa de tecnologia'])} focada em {random.choice(['transformação digital', 'soluções inovadoras', 'produtos escaláveis', 'experiência do cliente'])}.",
			f"\n\nNosso produto impacta {random.choice(['milhares', 'milhões'])} de usuários diariamente.",
		]
		context = random.choice(contexts)

		# Adiciona responsabilidades
		resp_list = self.areas[area]["responsibilities"]
		num_resp = min(random.randint(5, 7), len(resp_list))
		responsibilities = random.sample(resp_list, num_resp)
		resp_text = "\n\n**Responsabilidades:**\n" + "\n".join(f"• {r}" for r in responsibilities)

		# Adiciona informações extras para seniores
		extra = ""
		if level in ["Sênior", "Especialista"]:
			extra = "\n\n**Diferenciais do nível:**\n• Mentorar desenvolvedores júnior e pleno\n• Participar de definições arquiteturais estratégicas\n• Propor e liderar melhorias técnicas e de processo\n• Influenciar decisões de stack e tooling"

		return intro + context + resp_text + extra

	def _generate_skills(self, stack, stack_data):
		"""Gera skills obrigatórias e desejáveis."""
		# Required skills
		frameworks = random.sample(
			stack_data["frameworks"],
			min(random.randint(2, 4), len(stack_data["frameworks"]))
		)
		base_skills = stack_data["skills"][:5]
		required = [stack] + frameworks + base_skills

		# Nice to have
		optional = random.sample(
			stack_data.get("optional", []),
			min(random.randint(4, 6), len(stack_data.get("optional", [])))
		)

		return ", ".join(required), ", ".join(optional)

	def _generate_salary(self, seniority, contract_type):
		"""Gera faixa salarial baseada em senioridade e tipo de contrato."""
		# Faixas base para CLT
		ranges_clt = {
			Job.SeniorityChoices.JUNIOR: (3500, 6500),
			Job.SeniorityChoices.MID_LEVEL: (6500, 13000),
			Job.SeniorityChoices.SENIOR: (13000, 23000),
			Job.SeniorityChoices.SPECIALIST: (20000, 35000),
		}

		base_min, base_max = ranges_clt.get(seniority, (5000, 10000))

		# PJ ganha ~30-40% mais
		if contract_type == Job.ContractTypeChoices.PJ:
			base_min = int(base_min * 1.3)
			base_max = int(base_max * 1.4)

		# Adiciona variação aleatória
		min_sal = base_min + random.randint(-500, 1500)
		max_sal = base_max + random.randint(-1000, 4000)

		return min_sal, max_sal

	def _generate_benefits(self):
		"""Gera lista de benefícios."""
		num_benefits = random.randint(6, 12)
		benefits = random.sample(self.all_benefits, num_benefits)
		return "\n".join(f"• {b}" for b in benefits)


class Command(BaseCommand):
	help = "Cria vagas realistas usando Faker pt_BR."

	def add_arguments(self, parser):
		parser.add_argument(
			"--count",
			type=int,
			default=10,
			help="Quantidade de vagas a criar (padrão: 10)",
		)
		parser.add_argument(
			"--reset",
			action="store_true",
			help="Apaga todas as vagas existentes antes de criar.",
		)

	def handle(self, *args, count=10, reset=False, **opts):
		if reset:
			deleted, _ = Job.objects.all().delete()
			self.stdout.write(self.style.WARNING(f"🗑️  {deleted} vaga(s) removida(s)."))

		generator = JobGenerator()
		created = 0

		self.stdout.write(self.style.SUCCESS(f"\n🚀 Gerando {count} vagas...\n"))

		for i in range(count):
			job_data = generator.generate_job()
			job = Job.objects.create(**job_data)
			created += 1

			work_model_display = job.get_work_model_display()
			salary_info = ""
			if job.salary_visible:
				salary_info = f" | R$ {job.salary_min:,.0f}-{job.salary_max:,.0f}".replace(",", ".")

			self.stdout.write(
				f"  ✓ {job.title} | {work_model_display} | {job.location}{salary_info}"
			)

		self.stdout.write(self.style.SUCCESS(
			f"\n✅ {created} vaga(s) criada(s) com sucesso!"
		))


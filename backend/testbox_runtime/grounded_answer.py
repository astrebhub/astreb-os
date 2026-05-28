from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable

from .models import ApprovalState, DocumentProcessingState, LegalSource, RiskLevel


@dataclass(frozen=True)
class AnswerContext:
    language: str
    message: str
    domain: str
    domain_candidates: list[str]
    intent: str
    jurisdiction: str
    risk: RiskLevel
    sources: list[LegalSource]
    approval_state: ApprovalState
    document_text: str | None = None
    attachment_names: list[str] | None = None
    document_processing: DocumentProcessingState | None = None


def source_lines(sources: list[LegalSource]) -> str:
    return "\n\n".join(
        f"{number}. {source.title}\n{source.url}\n{source.summary}"
        for number, source in enumerate(sources, start=1)
    )


class GroundedAnswerComposer:
    """Builds source-bound orientation responses; it does not make routing decisions."""

    def __init__(self) -> None:
        self.intent_renderers: dict[str, Callable[[AnswerContext], str]] = {
            "introduce_system": self._introduction,
            "launch_regulated_energy_storage_manufacturing_business": self._energy_storage,
            "explain_cooperative_ua": self._cooperative_ua,
            "draft_letter": self._letter_intake,
            "review_document": self._document_intake,
            "build_action_plan": self._plan_intake,
            "prepare_event_participation": self._event_preparation,
            "forecast_event_challenges": self._event_challenge_forecast,
            "strategic_positioning": self._strategic_positioning,
            "assess_situation": self._situation_intake,
            "request_external_action": self._external_action_intake,
            "request_unapproved_external_execution": self._external_action_blocked,
        }
        self.domain_renderers: dict[str, Callable[[AnswerContext], str]] = {
            "liability": self._liability,
            "business_formation": self._business_formation,
            "social_housing": self._social_housing,
            "employment_contract": self._zero_hours_contract,
            "employment": self._employment,
            "zzp_intermediary_contract": self._zzp_intermediary_contract,
            "residential_parking": self._residential_parking,
            "consulting_services": self._consulting_services,
        }

    def compose(self, context: AnswerContext) -> str:
        renderer = self.intent_renderers.get(context.intent)
        if renderer is not None and context.intent in {
            "introduce_system",
            "draft_letter",
            "review_document",
            "build_action_plan",
            "prepare_event_participation",
            "forecast_event_challenges",
            "strategic_positioning",
            "assess_situation",
            "request_external_action",
            "request_unapproved_external_execution",
        }:
            return renderer(context)
        if context.domain != "general" and not context.sources:
            return self._missing_sources(context)
        if renderer is None:
            renderer = self.domain_renderers.get(context.domain)
        if renderer is not None:
            return renderer(context)
        if context.domain != "general":
            return self._source_bound_fallback(context)
        return self._general(context)

    def _missing_sources(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "1. Что удалось определить\n\n"
                f"Запрос относится к регулируемой теме: {context.domain}. Я могу "
                "зафиксировать тему и необходимые факты, но не могу выдавать "
                "подтверждённый правовой вывод без официальной опоры.\n\n"
                "2. Что не удалось проверить\n\n"
                "По этой теме в текущем реестре не найден подключённый официальный "
                "источник. Реестр источников требует расширения.\n\n"
                "3. Следующий шаг\n\n"
                "Укажите страну и практическую цель запроса либо приложите официальный "
                "документ; после этого можно продолжить ориентирование. До подключения "
                "источника вывод требует проверки человеком."
            )
        if context.language == "nl":
            return (
                "Ik herken een gereguleerde vraag, maar heb geen gekoppelde officiele "
                "bron gevonden. Daarom geef ik geen conclusie zonder onderbouwing. "
                "Verduidelijk land en rechtsgebied; menselijke controle is vereist."
            )
        return (
            "LegalBox cannot provide regulated orientation without connected official "
            "sources. Clarify jurisdiction/domain; human review is required."
        )

    def _liability(self, context: AnswerContext) -> str:
        sources = source_lines(context.sources)
        vehicle_stated = any(
            marker in context.message.casefold()
            for marker in ("авто", "машин", "car", "auto", "motor vehicle", "motorrijtuig")
        )
        if context.language == "nl":
            return (
                "1. Kort antwoord\n\n"
                "Als het ongeval in Nederland plaatsvond met een auto en een fietser, "
                "is de schadeclaim niet automatisch onrechtmatig omdat de fietser tegen "
                "de auto aanreed. Artikel 185 Wegenverkeerswet 1994 kan de eigenaar of "
                "houder aansprakelijk maken, tenzij overmacht aannemelijk is.\n\n"
                f"2. Bronnen\n\n{sources}\n\n"
                "3. Volgende stappen\n\nMeld de claim bij uw WA/autoverzekeraar, "
                "erken geen aansprakelijkheid zonder controle en verzamel bewijsmateriaal.\n\n"
                "Disclaimer: dit is informatieve juridische orientatie, geen definitief advies."
            )
        if context.language == "ru":
            if not vehicle_stated:
                return (
                    "1. Что важно уточнить сразу\n\n"
                    "Вы указали, что в вас врезался велосипедист в Нидерландах и требует "
                    "компенсацию, но не указали, были ли вы в автомобиле или другом "
                    "моторном транспортном средстве. Это ключевой факт: статья 185 "
                    "Wegenverkeerswet 1994 относится к ДТП с моторным транспортным "
                    "средством и велосипедистом.\n\n"
                    "2. Если вы были на автомобиле или мотоцикле\n\n"
                    "Требование велосипедиста не исключается только тем, что столкновение "
                    "произошло по его движению. Вопрос ответственности проверяется с "
                    "учётом Article 185, обстоятельств ДТП и возможного overmacht.\n\n"
                    f"3. Официальные источники\n\n{sources}\n\n"
                    "4. Следующие шаги\n\n"
                    "Уточните ваш вид транспорта; если это автомобиль/мотоцикл, передайте "
                    "требование страховщику и сохраните фото, свидетелей и переписку. "
                    "Не признавайте ответственность до проверки фактов.\n\n"
                    "Дисклеймер: это информационная правовая ориентация, а не решение по делу."
                )
            return (
                "1. Краткий ответ\n\n"
                "Если ДТП произошло в Нидерландах и участвовали автомобиль и велосипедист, "
                "требование о компенсации не становится незаконным только потому, что "
                "велосипедист врезался сам. Статья 185 Wegenverkeerswet 1994 может "
                "возлагать ответственность на владельца или держателя автомобиля, если "
                "не доказан overmacht.\n\n"
                f"2. Источники\n\n{sources}\n\n"
                "3. Следующие шаги\n\n"
                "1. Передайте требование автостраховщику.\n"
                "2. Не признавайте ответственность до проверки.\n"
                "3. Соберите фото, схему, свидетелей и переписку.\n\n"
                "Дисклеймер: это информационная правовая ориентация, а не решение по делу."
            )
        return self._source_bound_fallback(context)

    def _energy_storage(self, context: AnswerContext) -> str:
        if context.language != "ru":
            return (
                "This concerns both business formation and regulated battery or energy-storage "
                "manufacturing. Review the legal entity, EU Batteries Regulation, producer "
                "responsibility and possible environmental permits before market launch.\n\n"
                f"Official sources\n\n{source_lines(context.sources)}\n\n"
                "Disclaimer: informational orientation; obtain specialist review."
            )
        return (
            "1. Краткий вывод\n\n"
            "Запуск компании по производству накопителей энергии в Нидерландах или для "
            "рынка ЕС требует одновременно регистрации бизнеса и проверки регулируемого "
            "производства батарей. Для владения технологией, оборудования, договоров и "
            "привлечения инвестиций первым кандидатом для сравнения обычно будет BV.\n\n"
            "2. Обязательные блоки проверки\n\n"
            "1. Регистрация компании, владение IP и распределение ответственности.\n"
            "2. Регламент ЕС 2023/1542 о батареях: техническая документация, "
            "соответствие, маркировка и вывод продукта на рынок ЕС.\n"
            "3. Ответственность производителя при поставке батарей в Нидерландах.\n"
            "4. Экологические разрешения и уведомления для производственной площадки.\n\n"
            f"3. Официальные источники\n\n{source_lines(context.sources)}\n\n"
            "4. Следующий шаг\n\n"
            "Зафиксируйте тип накопителя, место производства, объём и рынок продаж, "
            "затем проверьте форму компании, product compliance, UPV и разрешения со "
            "специалистами до запуска.\n\n"
            "Дисклеймер: это информационная ориентация по официальным источникам "
            "Нидерландов и ЕС, а не юридическая или техническая консультация."
        )

    def _business_formation(self, context: AnswerContext) -> str:
        if context.language != "ru":
            return self._source_bound_fallback(context)

        value = context.message.casefold()
        if "консалт" in value or "consult" in value:
            return (
                "1. Что удалось определить\n\n"
                "Вы спрашиваете о форме компании для консалтинговой деятельности. "
                "Страна регистрации, число основателей, договорная ответственность и "
                "планы найма в запросе не указаны. Подключённые официальные источники "
                "относятся к Нидерландам, поэтому сравнение ниже является ориентиром "
                "для Нидерландов, а не автоматически выбранной юрисдикцией.\n\n"
                "2. Формы, которые имеет смысл сравнить\n\n"
                "- Если консультант работает один, следует сравнить индивидуальную "
                "форму деятельности и BV. BV является отдельным юридическим лицом, "
                "но требует нотариального оформления и дополнительных обязательств.\n"
                "- Если консультантов несколько, официальный источник предлагает "
                "сравнивать partnership/VOF, BV и cooperative с учётом ответственности "
                "и налогов.\n"
                "- Cooperative релевантен не автоматически, а когда несколько "
                "предпринимателей действительно работают коллективно.\n\n"
                "3. Что не следует предполагать\n\n"
                "- В запросе нет данных о разработке программного обеспечения или владении IP.\n"
                "- Нет данных, что бизнес запускает группа партнёров.\n"
                "- Нет данных о привлечении инвесторов.\n\n"
                f"4. Официальные источники (Нидерланды)\n\n{source_lines(context.sources)}\n\n"
                "5. Что нужно для предметного выбора\n\n"
                "Укажите страну регистрации, один вы или с партнёрами, ожидаемый риск "
                "по клиентским договорам и планируются ли сотрудники. После этого можно "
                "сузить выбор формы без выдуманных предположений.\n\n"
                "Дисклеймер: это информационная бизнес-ориентация по подключённым "
                "источникам, не персональная юридическая или налоговая рекомендация."
            )

        if "разработ" in value or "developer" in value:
            return (
                "1. Что следует сравнить\n\n"
                "Вы спрашиваете о форме компании для группы разработчиков и прямо "
                "сравниваете BV с кооперативом. В Нидерландах BV обычно сравнивают с "
                "cooperative по ответственности, управлению, возможности входа и выхода "
                "участников и планам финансирования.\n\n"
                "2. Практические различия\n\n"
                "- BV является отдельным юридическим лицом; она может быть удобна, если "
                "команда хочет фиксированные доли или в будущем принимать инвесторов.\n"
                "- Cooperative может подходить, если самостоятельные участники совместно "
                "берут проекты и нужна более гибкая модель членства.\n"
                "- Если команда создаёт код или иной IP, отдельно зафиксируйте, будет ли "
                "он принадлежать компании или передаваться ей участниками; из самого "
                "запроса наличие общего IP ещё не следует.\n\n"
                f"3. Официальные источники (Нидерланды)\n\n{source_lines(context.sources)}\n\n"
                "4. Следующий шаг\n\n"
                "Уточните страну регистрации, модель работы участников, планы инвестиций "
                "и предполагаемое владение результатами разработки; после этого можно "
                "сравнить BV и cooperative предметно.\n\n"
                "Дисклеймер: это информационная бизнес-ориентация, не персональная "
                "юридическая или налоговая рекомендация."
            )

        if any(
            marker in value
            for marker in ("программ", "software", "продуктовый ip", "кооператив", "cooperat")
        ):
            return (
                "1. Краткий вывод\n\n"
                "В запросе указана работа с программным обеспечением, продуктом или "
                "кооперативной моделью. Для такого сценария в Нидерландах обычно следует "
                "сравнить BV и кооператив: BV может подходить для владения продуктом, "
                "долей и привлечения инвестиций. Кооператив может подходить для "
                "коллективной работы самостоятельных участников.\n\n"
                f"2. Официальные источники\n\n{source_lines(context.sources)}\n\n"
                "3. Следующий шаг\n\n"
                "Уточните, кто владеет продуктом или IP, как распределяются голоса и "
                "доход, могут ли участники выходить и планируются ли инвесторы; затем "
                "сравните BV и cooperatie UA с нотариусом и налоговым консультантом.\n\n"
                "Дисклеймер: это информационная ориентация, не персональная рекомендация."
            )

        return (
            "1. Что удалось определить\n\n"
            "Вы выбираете организационно-правовую форму компании. Вид деятельности, "
            "страна регистрации, число основателей и предполагаемые обязательства пока "
            "не уточнены, поэтому называть одну форму лучшей преждевременно.\n\n"
            "2. Ориентир по подключённым источникам\n\n"
            "Источники по Нидерландам указывают, что форма влияет на ответственность и "
            "налоговые обязательства; среди вариантов для совместного старта названы "
            "VOF, BV, professional partnership и cooperative.\n\n"
            f"3. Официальные источники (Нидерланды)\n\n{source_lines(context.sources)}\n\n"
            "4. Следующий шаг\n\n"
            "Укажите страну, вид деятельности, один основатель или несколько, а также "
            "ожидаемый уровень договорной ответственности. Тогда сравнение будет "
            "относиться к вашей ситуации, а не к шаблонному сценарию.\n\n"
            "Дисклеймер: это информационная бизнес-ориентация, не персональная рекомендация."
        )

    def _cooperative_ua(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "1. Что означает cooperatie UA\n\n"
                "`Cooperatie UA` означает кооператив с исключённой ответственностью "
                "участников: `Uitgesloten van Aansprakelijkheid`. При форме UA участники "
                "не отвечают по долгам кооператива, включая ситуацию банкротства, если "
                "это закреплено в уставе.\n\n"
                "2. Варианты ответственности\n\n"
                "- `UA` - ответственность участников исключена.\n"
                "- `BA` - ответственность участников ограничена суммой в уставе.\n"
                "- `WA` - участники несут установленную ответственность по долгам.\n\n"
                "3. Важное ограничение\n\n"
                "UA не отменяет ответственность директора при ненадлежащем управлении "
                "и не защищает от личных гарантий или собственных нарушений.\n\n"
                f"4. Официальный источник\n\n{source_lines(context.sources)}\n\n"
                "5. Следующий шаг\n\n"
                "Сравните cooperatie UA с BV по владению IP, инвестициям, членству, "
                "голосованию и распределению доходов вместе с нидерландским нотариусом.\n\n"
                "Дисклеймер: это информационная ориентация по официальному источнику."
            )
        return self._source_bound_fallback(context)

    def _social_housing(self, context: AnswerContext) -> str:
        if context.language == "ru":
            refusal_orientation = (
                "\n\n4. Если уже получен отказ\n\n"
                "Запросите письменную причину отказа у woningcorporatie или gemeente, "
                "сверьте её с условиями регистрации, дохода и состава домохозяйства, "
                "и проверьте указанную в решении процедуру жалобы или пересмотра. "
                "Если ситуация срочная, отдельно уточните в gemeente возможность "
                "`urgentieverklaring`.\n\n"
                "5. Следующий шаг\n\nПередайте текст отказа без BSN и лишних "
                "персональных данных либо укажите gemeente, доход и состав семьи; "
                "тогда можно разобрать основание отказа по подключённым источникам."
                if "отказ" in context.message.casefold()
                else (
                    "\n\n4. Следующий шаг\n\nУкажите город, состав домохозяйства и "
                    "примерный годовой доход для предметной проверки."
                )
            )
            return (
                "1. Краткий ответ\n\n"
                "Для Нидерландов право на социальную аренду зависит от дохода, состава "
                "домохозяйства, регистрации в woningcorporatie и местных правил. "
                "Юрисдикция определена как предполагаемая, пока вы не указали муниципалитет.\n\n"
                "2. Основные ориентиры на 2026 год\n\n"
                "- Доход: до €51 537 для одного человека или до €56 910 для нескольких.\n"
                "- Максимальная базовая социальная аренда: €932,93 в месяц.\n"
                "- При срочной ситуации можно проверять условия urgentieverklaring.\n\n"
                f"3. Официальные источники\n\n{source_lines(context.sources)}"
                f"{refusal_orientation}\n\n"
                "Дисклеймер: это информационная ориентация, не решение о предоставлении жилья."
            )
        return self._source_bound_fallback(context)

    def _zero_hours_contract(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "1. Что это значит\n\n"
                "В Нидерландах «нулевой контракт» обычно означает `nulurencontract`: "
                "трудовой договор по вызову без заранее фиксированного количества часов.\n\n"
                "2. Что проверить\n\n"
                "- Вызов на работу обычно должен поступить минимум за 4 дня.\n"
                "- В предусмотренных случаях вызов оплачивается минимум за 3 часа.\n"
                "- После 12 месяцев работодатель должен предложить фиксированные часы "
                "на основе среднего объёма работы.\n"
                "- Вам положены отпуск и как минимум 8% vakantiegeld.\n\n"
                f"3. Официальные источники\n\n{source_lines(context.sources)}\n\n"
                "4. Следующий шаг\n\nПроверьте ставку, CAO, правила вызова и отмены "
                "смен до подписания договора.\n\n"
                "Дисклеймер: это информационная ориентация по источникам Нидерландов."
            )
        if context.language == "nl":
            return (
                "1. Wat dit betekent\n\n"
                "Een `nulurencontract` is in Nederland een oproepovereenkomst zonder "
                "vooraf afgesproken vast aantal uren. U werkt wanneer u wordt opgeroepen.\n\n"
                "2. Belangrijke risico's en controles\n\n"
                "- Uw inkomen en rooster kunnen minder voorspelbaar zijn.\n"
                "- Een oproep moet doorgaans minimaal 4 dagen vooraf plaatsvinden.\n"
                "- In bepaalde gevallen heeft u per oproep recht op minimaal 3 uur loon.\n"
                "- Na 12 maanden moet de werkgever vaste uren aanbieden op basis van "
                "het gemiddelde aantal gewerkte uren.\n"
                "- U bouwt vakantie-uren op en heeft recht op minimaal 8% vakantiegeld.\n\n"
                f"3. Officiele bronnen\n\n{source_lines(context.sources)}\n\n"
                "4. Voor u tekent\n\nControleer het uurloon, de CAO, regels voor "
                "oproepen en annulering, en of de onzekerheid over uren bij uw situatie past.\n\n"
                "Disclaimer: dit is informatieve orientatie op basis van Nederlandse "
                "officiele bronnen, geen individueel juridisch advies."
            )
        return self._source_bound_fallback(context)

    def _employment(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "1. Краткий ответ\n\n"
                "Поскольку страна не указана, я использую источники Нидерландов как "
                "рабочую ориентацию, а не подтверждённую юрисдикцию. При невыплате "
                "зарплаты работник может письменно потребовать выплату задолженности "
                "и при необходимости обратиться за юридической помощью. Rijksoverheid "
                "указывает этот порядок как официальный следующий шаг.\n\n"
                f"2. Официальные источники\n\n{source_lines(context.sources)}\n\n"
                "3. Следующий шаг\n\nСохраните договор, расчётные листки, график и "
                "переписку; направьте письменное требование работодателю.\n\n"
                "Дисклеймер: это информационная правовая ориентация, а не юридический совет."
            )
        return self._source_bound_fallback(context)

    def _zzp_intermediary_contract(self, context: AnswerContext) -> str:
        if context.language != "ru":
            return self._source_bound_fallback(context)
        return (
            "1. Что происходит в вашей ситуации\n\n"
            "Вы хотите работать как `zzp` через агентство трудоустройства и заключить "
            "с ним договор на оказание услуг. Термин `zzp` указывает на нидерландский "
            "контекст, поэтому ниже даю ориентацию по официальным источникам "
            "Нидерландов; подтвердите страну, если договор будет в другой юрисдикции.\n\n"
            "2. Сначала определите роль агентства\n\n"
            "- `Bemiddeling` (посредничество): агентство только сводит вас с клиентом; "
            "договор на саму работу заключается между вами и конечным клиентом.\n"
            "- `Tussenkomst` (работа через посредника): агентство является вашим "
            "заказчиком, а вы выполняете задание для его клиента.\n\n"
            "Это не формальность: от модели зависит, с кем у вас договор, кому вы "
            "выставляете счёт и как проверяется риск скрытых трудовых отношений.\n\n"
            "3. Что проверить до подписания\n\n"
            "- кто указан заказчиком и кто оплачивает ваши счета;\n"
            "- может ли агентство или конечный клиент руководить способом выполнения работы;\n"
            "- разрешены ли другие заказчики и нет ли чрезмерного запрета конкуренции;\n"
            "- кто несёт риск неоплаты, ответственность и расходы на инструменты;\n"
            "- указаны ли KVK/BTW-данные, тариф, срок оплаты, прекращение и страхование.\n\n"
            "4. Governance-риск\n\n"
            "По Wet DBA статус определяется не только текстом договора, но и фактической "
            "работой. Если вы фактически работаете под руководством как сотрудник, "
            "возможен риск `schijnzelfstandigheid` (ложной самозанятости).\n\n"
            f"5. Официальные источники\n\n{source_lines(context.sources)}\n\n"
            "6. Следующий шаг\n\n"
            "Пришлите проект договора или укажите: агентство только находит клиента "
            "или само будет вашим заказчиком; кто определяет график и способ работы; "
            "можно ли работать с другими клиентами. Тогда DocumentBox проверит конкретные "
            "пункты договора.\n\n"
            "Дисклеймер: это информационная бизнес- и договорная ориентация, "
            "не персональная юридическая или налоговая рекомендация."
        )

    def _consulting_services(self, context: AnswerContext) -> str:
        if context.language != "ru":
            return self._source_bound_fallback(context)
        return (
            "1. Что удалось определить\n\n"
            "Вы хотите начать оказывать консалтинговые услуги в рамках консалтинговой деятельности. Вид консультаций и "
            "страна не указаны; поскольку подключённые официальные источники относятся "
            "к Нидерландам, ниже приведена ориентация для Нидерландов как предполагаемой "
            "юрисдикции.\n\n"
            "2. Что обычно необходимо для старта в Нидерландах\n\n"
            "1. Определить услугу и ограничения: управленческий, IT, маркетинговый или "
            "другой консалтинг; для финансовых, юридических и иных регулируемых "
            "консультаций могут действовать специальные требования.\n"
            "2. Выбрать форму деятельности: при работе одному сравнить `eenmanszaak` "
            "и `BV`; при совместной работе также рассмотреть partnership или cooperative.\n"
            "3. Зарегистрировать бизнес в `KVK`. По официальному плану регистрации KVK "
            "передаёт данные в `Belastingdienst`; при признании VAT-entrepreneur вы "
            "получаете номер `BTW`/VAT ID.\n"
            "4. Организовать учёт, счета и договор с клиентом: объём услуг, результат, "
            "тариф, сроки оплаты, конфиденциальность, ответственность и прекращение.\n"
            "5. Оценить профессиональную ответственность: для совета, ошибка в котором "
            "может вызвать финансовый ущерб клиента, Business.gov.nl указывает на "
            "`beroepsaansprakelijkheidsverzekering` (`BAV`).\n\n"
            "3. Что не следует предполагать\n\n"
            "- В запросе нет данных о разработке программного обеспечения или владении IP.\n"
            "- Нет данных о партнёрах, сотрудниках или инвесторах.\n"
            "- Нельзя утверждать, нужна ли лицензия, пока не указан вид консалтинга.\n\n"
            f"4. Официальные источники (Нидерланды)\n\n{source_lines(context.sources)}\n\n"
            "5. Что уточнить для следующего шага\n\n"
            "Напишите, в какой сфере будут консультации, в какой стране вы будете "
            "регистрироваться, будете работать один или с партнёрами и кто ваши "
            "клиенты: частные лица или компании. Тогда можно предметно определить "
            "форму, договоры, страхование и возможное специальное регулирование.\n\n"
            "Дисклеймер: это информационная бизнес-ориентация по официальным "
            "источникам Нидерландов, не персональная юридическая или налоговая рекомендация."
        )

    def _residential_parking(self, context: AnswerContext) -> str:
        if context.language != "ru":
            return self._source_bound_fallback(context)
        return (
            "1. Куда обращаться\n\n"
            "Если речь о Нидерландах, начните с вашей `gemeente` или местной службы "
            "парковки (`parkeerbeheer`). Правила парковки и разрешений устанавливаются "
            "по муниципалитетам, поэтому без города нельзя определить точную процедуру "
            "и форму заявления.\n\n"
            "2. Уточните, что именно вам нужно\n\n"
            "- разрешение жителя на парковку в зоне платной/разрешительной парковки "
            "(`bewonersparkeervergunning`);\n"
            "- персонально зарезервированное место у дома: обычно такой вопрос требует "
            "специального основания, например места для человека с инвалидностью "
            "на номер автомобиля;\n"
            "- место для зарядки электромобиля или иное изменение улицы: это отдельная "
            "муниципальная процедура.\n\n"
            "3. План действий\n\n"
            "1. Назовите город/муниципалитет и тип запроса из списка выше.\n"
            "2. Откройте раздел parkeren/parkeervergunning на сайте gemeente или "
            "обратитесь в parkeerbeheer.\n"
            "3. Подготовьте адрес регистрации, номер автомобиля и, если требуется "
            "персональное место, документ об основании запроса.\n"
            "4. Проверьте стоимость, срок действия, зону и возможность ожидания/отказа.\n\n"
            f"4. Официальный ориентир для Нидерландов\n\n{source_lines(context.sources)}\n\n"
            "5. Что нужно от вас сейчас\n\n"
            "Напишите город и уточните: нужна обычная парковочная vergunning для "
            "жителя или зарезервированное место именно у дома. После этого я покажу "
            "точный муниципальный маршрут.\n\n"
            "Дисклеймер: это ориентация по процедуре; решение о месте или разрешении "
            "принимает соответствующая gemeente."
        )

    def _source_bound_fallback(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "1. Правовая ориентация по официальным источникам\n\n"
                f"Область: {context.domain}. Юрисдикция: {context.jurisdiction}.\n\n"
                f"2. Источники\n\n{source_lines(context.sources)}\n\n"
                "3. Следующий шаг\n\nПроверьте факты по источникам и запросите "
                "проверку специалистом перед принятием решения.\n\n"
                "Дисклеймер: это информационная ориентация, а не юридический совет."
            )
        return (
            f"Source-bound orientation for {context.domain} in {context.jurisdiction}.\n\n"
            f"Official sources\n\n{source_lines(context.sources)}\n\n"
            "Disclaimer: informational orientation, not legal advice."
        )

    def _letter_intake(self, context: AnswerContext) -> str:
        if context.language == "ru":
            value = context.message.casefold()
            if "работодател" in value and (
                "невыплат" in value or "не выплат" in value or "зарплат" in value
            ):
                sources = (
                    f"\n\nОфициальная опора для проверки: \n{source_lines(context.sources)}"
                    if context.sources
                    else ""
                )
                return (
                    "Ниже черновик письма о невыплате зарплаты. Заполните поля в "
                    "квадратных скобках перед отправкой.\n\n"
                    "Тема: Требование о выплате задолженности по заработной плате\n\n"
                    "Уважаемый(ая) [имя работодателя/HR],\n\n"
                    "По состоянию на [дата] мне не выплачена заработная плата за "
                    "[период] в размере [сумма] EUR, подлежащая выплате согласно "
                    "[трудовому договору/расчётному листку] не позднее [дата выплаты].\n\n"
                    "Прошу выплатить задолженность и предоставить расчётный листок не "
                    "позднее [срок, например 5 рабочих дней] на известный вам банковский "
                    "счёт. Если платёж уже произведён, прошу направить подтверждение.\n\n"
                    "При отсутствии оплаты или обоснованного ответа в указанный срок я "
                    "оставляю за собой право обратиться за юридической помощью для "
                    "взыскания задолженности и применимых последствий просрочки.\n\n"
                    "С уважением,\n[ФИО]\n[контактные данные]\n[дата]\n\n"
                    "Что проверить перед отправкой: период и сумму долга, договорную "
                    "дату выплаты, наличие payslip и страну применимого трудового права."
                    f"{sources}\n\n"
                    "Дисклеймер: это черновик требования, а не окончательная юридическая позиция."
                )
            return (
                "Хорошо, подготовим письмо.\n\n"
                "Начальный черновик\n\n"
                "Тема: [цель письма]\n\n"
                "Уважаемый(ая) [адресат],\n\n"
                "Обращаюсь по вопросу [кратко опишите ситуацию]. Прошу [нужный "
                "результат] до [срок, если нужен].\n\n"
                "С уважением,\n[имя]\n[контактные данные]\n\n"
                "Чтобы заменить поля конкретным готовым текстом, пришлите:\n"
                "1. Кому письмо: организация или имя адресата.\n"
                "2. Цель: что вы просите, сообщаете или оспариваете.\n"
                "3. Ключевые факты: даты, номер дела/договора, суммы или срок ответа.\n"
                "4. Язык письма: русский, нидерландский или английский.\n"
                "5. Тон: вежливый, официальный или требовательный.\n\n"
                "Например: «Письмо работодателю на нидерландском: не выплачена зарплата "
                "за апрель, прошу оплатить до 30 мая, тон официальный».\n\n"
                "Если письмо касается закона, долга, договора или госоргана, я сначала "
                "определю нужные официальные источники и отмечу, где требуется проверка."
            )
        if context.language == "nl":
            return (
                "Goed, ik help u een brief opstellen. Stuur de ontvanger, het doel, "
                "de belangrijkste feiten en datums, de gewenste taal en de toon. "
                "Bij een juridische of financiele brief controleer ik eerst welke "
                "officiele bronnen en menselijke beoordeling nodig zijn."
            )
        return (
            "Good, I can prepare a letter. Send the recipient, purpose, key facts and "
            "dates, desired language, and tone. For a legal or financial letter I will "
            "first determine the required official sources and review level."
        )

    def _introduction(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Привет. Я TESTBOX Administrator - рабочий интерфейс AI Cabinet.\n\n"
                "Я могу помочь разобрать ситуацию, составить план действий, "
                "проверить документ или подготовить письмо. Для вопросов о законах, "
                "работе, деньгах, пребывании, ДТП и компенсации я определяю "
                "юрисдикцию и тему, использую подключенные официальные источники "
                "и показываю, когда нужна проверка человеком.\n\n"
                "Отдельно подключен ASTI - управляемый слой внешних действий. "
                "Он может выполнять отправки только после создания действия, "
                "явного одобрения и отдельной команды execute; я не отправляю "
                "сообщения наружу самостоятельно.\n\n"
                "С чего начнем? Опишите задачу или прикрепите документ."
            )
        if context.language == "nl":
            return (
                "Hallo. Ik ben TESTBOX Administrator, de werkinterface van AI Cabinet. "
                "Ik kan een situatie analyseren, een stappenplan maken, een document "
                "controleren of een brief voorbereiden. Externe acties via ASTI worden "
                "alleen uitgevoerd na expliciete goedkeuring."
            )
        return (
            "Hello. I am TESTBOX Administrator, the working interface for AI Cabinet. "
            "I can analyze a situation, build an action plan, review a document, or "
            "prepare a letter. External actions through ASTI run only after explicit "
            "approval and a separate governed execute step."
        )

    def _external_action_intake(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Я могу подготовить внешнее действие через ASTI, но не отправлю "
                "сообщение напрямую из чата.\n\n"
                "Безопасный порядок: создать action с текстом и адресатом, показать "
                "его вам для проверки, получить явное одобрение и только затем "
                "выполнить отправку с записью в audit.\n\n"
                "Укажите канал, получателя и черновик текста. Отправка останется "
                "заблокированной до вашего approve."
            )
        return (
            "I can prepare an external action through ASTI, but I cannot send it "
            "directly from chat. Provide the channel, recipient and draft; delivery "
            "remains blocked until explicit approval and governed execution."
        )

    def _external_action_blocked(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Отправка без подтверждения заблокирована.\n\n"
                "ASTI не выполняет внешние действия по команде, обходящей approval. "
                "Для отправки нужен отдельный pending action, проверка текста и "
                "получателя, явное одобрение оператора и только затем execute.\n\n"
                "Никакое сообщение не отправлено. Если требуется отправка, подтвердите "
                "ранее созданное действие через утверждённый процесс."
            )
        if context.language == "nl":
            return (
                "Verzending zonder goedkeuring is geblokkeerd. ASTI voert geen externe "
                "actie uit zonder expliciete approval en een afzonderlijke execute-stap. "
                "Er is niets verstuurd."
            )
        return (
            "Delivery without approval is blocked. ASTI does not execute external "
            "actions without explicit approval and a separate execute step. Nothing was sent."
        )

    def _active_document_analysis_ru(self, context: AnswerContext) -> str:
        text = (context.document_text or "").strip()
        value = text.casefold()
        request_value = context.message.casefold()
        payment_deadline_focus = bool(
            "только" in request_value
            and any(marker in request_value for marker in ("срок", "оплат", "payment", "deadline"))
        )
        findings: list[str] = []
        missing: list[str] = []
        risks: list[str] = []

        if not payment_deadline_focus and ("contract" in value or "договор" in value):
            findings.append("Документ обозначен как договор/contract.")
        elif not payment_deadline_focus:
            missing.append("тип документа не определён из извлечённого фрагмента")

        employer = re.search(r"(?:employer|работодатель)\s*:\s*([^\n]+)", text, re.I)
        employee = re.search(r"(?:employee|работник|исполнитель)\s*:\s*([^\n]+)", text, re.I)
        if employer and not payment_deadline_focus:
            findings.append(f"Указана сторона работодателя/заказчика: {employer.group(1).strip()}")
        if employee and not payment_deadline_focus:
            findings.append(f"Указана сторона работника/исполнителя: {employee.group(1).strip()}")
        if (not employer or not employee) and not payment_deadline_focus:
            missing.append("полные данные обеих сторон")

        amount = re.search(
            r"(?:EUR|€)\s*[\d][\d\s.,]*|[\d][\d\s.,]*\s*(?:EUR|€)",
            text,
            re.I,
        )
        if amount:
            findings.append(f"Найдена сумма: {amount.group(0).strip().rstrip('.,;')}.")
            risks.append("Сумма обнаружена; нужно сверить, за какую услугу и с НДС или без НДС она указана.")
        else:
            missing.append("сумма и валюта оплаты")

        payment_due = re.search(
            r"(?:payment\s+due(?:\s+on)?|оплат\w*\s+до|срок\s+оплаты\s*:?)\s*"
            r"([0-9]{1,2}\s+[A-Za-zА-Яа-я]+\s+[0-9]{4}|[0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4})",
            text,
            re.I,
        )
        if payment_due:
            findings.append(f"Найден срок оплаты: {payment_due.group(1).strip()}.")
            risks.append("Срок оплаты найден; если он прошёл, следует проверить условие просрочки и основания требования.")
        else:
            missing.append("точный срок оплаты или правило выставления счёта")

        termination = re.search(
            r"(?:termination\s+notice|notice\s+period|срок\s+уведомления|расторжен\w*)"
            r"\s*:?\s*([0-9]+\s*(?:days?|дн(?:ей|я)?|months?|месяц\w*))",
            text,
            re.I,
        )
        if termination:
            findings.append(f"Найден срок уведомления о прекращении: {termination.group(1).strip()}.")
            risks.append("Есть условие прекращения; нужно сверить, для какой стороны оно действует и с какого момента считается.")
        else:
            missing.append("условия прекращения или расторжения")

        penalty = re.search(
            r"(?:penalty|late fee|interest|штраф|пен[яи]|процент)\s*:?\s*"
            r"([^\n.;]{1,50})",
            text,
            re.I,
        )
        if penalty:
            clause = penalty.group(0).strip().rstrip(".,;")
            findings.append(f"Найдено условие о штрафе/процентах: {clause}.")
            risks.append("Есть финансовая санкция; нужно проверить основание, размер и применимость при просрочке.")
        else:
            missing.append("штрафы/проценты при просрочке")

        governing_law = re.search(
            r"(?:governing law|applicable law|применим\w+ прав\w*)\s*:?\s*([^\n.;]{2,80})",
            text,
            re.I,
        )
        if governing_law and not payment_deadline_focus:
            findings.append(f"Указано применимое право: {governing_law.group(1).strip()}.")
            risks.append("Применимое право найдено; правовые выводы должны проверяться в этой юрисдикции.")
        elif not payment_deadline_focus:
            missing.append("применимое право и суд/споры")

        if not payment_deadline_focus and not re.search(r"signature|signed|подпис", text, re.I):
            missing.append("подписи или подтверждение согласия")

        findings_lines = "\n".join(f"- {finding}" for finding in findings) or "- Читаемые факты пока не обнаружены."
        risk_lines = "\n".join(f"- {risk}" for risk in risks) or "- Конкретные финансовые или сроковые риски из фрагмента не подтверждены."
        missing_lines = "\n".join(f"- {item}" for item in missing)
        focus_note = (
            "Фокус анализа: только сроки и оплата; сведения вне этого фокуса не оцениваются.\n\n"
            if payment_deadline_focus
            else "Проверка выполняется по выбранным направлениям: содержание, риски, оплата и сроки.\n\n"
            if any(
                signal in context.message.casefold()
                for signal in ("краткое объяснение", "поиск рисков", "проверка оплаты", "оплаты/сроков")
            )
            else ""
        )
        extraction_note = ""
        if context.document_processing and context.document_processing.confidence is not None:
            extraction_note = (
                f" Извлечение выполнено методом {context.document_processing.method}; "
                f"оценка уверенности: {context.document_processing.confidence:.0%}."
            )
        return (
            f"{focus_note}1. Найденные данные\n\n{findings_lines}\n\n"
            f"2. Выявленные риски\n\n{risk_lines}\n\n"
            f"3. Чего не хватает в доступном тексте\n\n{missing_lines}\n\n"
            "4. Ограничения анализа\n\n"
            f"Проверка основана только на извлечённом тексте ({len(text)} знаков)."
            f"{extraction_note} "
            "Я не подтверждаю юридические последствия, пока не известны полный текст, "
            "страна/применимое право и качество извлечения.\n\n"
            "5. Следующий шаг\n\n"
            "Загрузите полный читаемый документ или укажите юрисдикцию договора; "
            "тогда можно проверить просрочку, требование об оплате и проект ответа."
        )

    def _document_intake(self, context: AnswerContext) -> str:
        attachments = context.attachment_names or []
        focus_requested = any(
            signal in context.message.casefold()
            for signal in ("краткое объяснение", "поиск рисков", "проверка оплаты", "оплаты/сроков")
        )
        extraction_unavailable = bool(
            context.document_processing and context.document_processing.ocr_required
        ) or bool(
            context.document_text
            and (
                "text was not extractable" in context.document_text.lower()
                or "ocr is not active" in context.document_text.lower()
            )
        )
        if context.language == "ru":
            if attachments and extraction_unavailable:
                return (
                    "1. Попытка анализа\n\n"
                    f"Документ получен в DocumentBox: {', '.join(attachments)}.\n\n"
                    "2. Найденные данные\n\n"
                    "Файл прикреплён, но из него пока не удалось извлечь читаемый текст. "
                    "Для PDF это обычно означает скан или формат потока, который текущий "
                    "локальный извлекатель не распознаёт.\n\n"
                    "3. Ограничения анализа\n\n"
                    "Содержательные данные, суммы и сроки не подтверждены; я не буду "
                    "придумывать содержание документа.\n\n"
                    "4. Следующий шаг\n\n"
                    "Загрузите текстовый PDF/DOCX/TXT либо текст после OCR. После "
                    "извлечения текста DocumentBox сразу выполнит проверку обязательств, "
                    "дат, сумм, оплаты и условий прекращения."
                )
            if context.document_text:
                return self._active_document_analysis_ru(context)
            if attachments:
                return (
                    "1. Попытка анализа\n\n"
                    f"Документ получен в DocumentBox: {', '.join(attachments)}.\n\n"
                    "2. Найденные данные\n\n"
                    "Вложение зарегистрировано, но текст для проверки не получен.\n\n"
                    "3. Ограничения анализа\n\n"
                    "Без читаемого текста нельзя подтвердить содержание, риски, оплату "
                    "или сроки.\n\n"
                    "4. Следующий шаг\n\n"
                    "Загрузите документ с доступным текстом либо результат OCR."
                )
            return (
                "Хорошо, проверим документ.\n\n"
                "1. Попытка анализа\n\n"
                "Я запустил DocumentBox, но документ или извлечённый текст не передан.\n\n"
                "2. Что удалось проверить\n\n"
                "Содержательные выводы невозможны без файла: факты, суммы и сроки "
                "пока не подтверждены.\n\n"
                "3. Следующий шаг\n\n"
                "Загрузите файл или фото. После получения читаемого текста я сразу "
                "выделю смысл, риски, сроки, суммы, подписи и возможный проект ответа. "
                "Чувствительные данные можно предварительно скрыть."
            )
        if attachments and extraction_unavailable:
            return (
                f"The document has been received and routed to DocumentBox: {', '.join(attachments)}. "
                "No readable text could be extracted yet, so I cannot review its contents "
                "without inventing them. Upload a text-readable file or OCR output to proceed."
            )
        if context.document_text:
            if focus_requested:
                return (
                    "Continuing the document review for the selected focus areas.\n\n"
                    f"Extracted passage:\n{context.document_text.strip()[:1000]}\n\n"
                    "Review payments, deadlines, termination terms, liabilities and governing "
                    "law against the full readable document before relying on a conclusion."
                )
            return (
                "The document has been received and routed to DocumentBox for structured "
                "review. I can examine obligations, deadlines, payment terms, termination "
                "conditions, and risk points. For legal consequences or material financial "
                "risk, jurisdiction and human review may still be required."
            )
        if attachments:
            return (
                f"The document has been received and routed to DocumentBox: {', '.join(attachments)}. "
                "No document text is available yet; provide readable text or OCR output for review."
            )
        return "Please attach the document and state what should be checked: meaning, risks, deadlines, amounts, or a response draft."

    def _plan_intake(self, context: AnswerContext) -> str:
        if context.language == "ru":
            if context.domain == "residential_parking":
                return self._residential_parking(context)
            if context.domain == "event_collaboration":
                return self._event_preparation(context)
            return (
                "Начальный план действий\n\n"
                "1. Зафиксировать требуемый результат и срок.\n"
                "2. Собрать подтверждающие факты и документы.\n"
                "3. Определить ограничения и риск решения.\n"
                "4. Выполнить следующий практический шаг и зафиксировать результат.\n\n"
                "Чтобы сделать план предметным, опишите цель, ситуацию, срок и "
                "ограничения. Для регулируемой темы я добавлю официальные источники."
            )
        return "Describe your objective, current situation, deadline, and constraints; I will structure an action plan."

    def _event_preparation(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "План подготовки к Pre-Hackathon: OneGov #2\n\n"
                "Цель встречи: познакомиться с challenges и выйти с понятным выбором "
                "команды или направлений для следующего шага.\n\n"
                "До мероприятия\n\n"
                "1. Подготовьте самопрезентацию на 30 секунд: кто вы, какие задачи умеете "
                "решать и какой вклад хотите внести.\n"
                "2. Сформулируйте 2-3 сильные стороны для команды: например, AI/governance, "
                "исследование, дизайн сервиса, разработка, данные или презентация.\n"
                "3. Подготовьте три вопроса к challenges: для кого проблема, как измеряется "
                "результат и какие данные/ограничения уже известны.\n"
                "4. Возьмите способ быстро обменяться контактом: LinkedIn/QR или короткий профиль.\n\n"
                "Во время встречи\n\n"
                "5. Сначала прослушайте challenges и отметьте максимум два, где совпадают "
                "ваш интерес и практический вклад.\n"
                "6. При знакомстве с участниками используйте формулу: «Мне интересен challenge X; "
                "я могу помочь с Y; ищу команду, где нужен Z».\n"
                "7. Перед присоединением к команде уточните: цель, роли, язык работы, "
                "ожидаемый результат и канал связи.\n\n"
                "После встречи\n\n"
                "8. В тот же день отправьте выбранной команде короткое подтверждение: "
                "ваша роль, первый вклад и следующий созвон/дедлайн.\n"
                "9. Если команда ещё не выбрана, сохраните два наиболее подходящих challenge "
                "и напишите организатору или участникам с конкретным предложением вклада.\n\n"
                "Практический следующий шаг сейчас: напишите мне ваши 3 навыка и интерес "
                "(например AI governance, civic tech, research или development), и я подготовлю "
                "короткую самопрезентацию и вопросы для OneGov #2."
            )
        if context.language == "nl":
            return (
                "Voorbereidingsplan voor Pre-Hackathon: OneGov #2\n\n"
                "Doel: de challenges leren kennen en vertrekken met een passend team of "
                "een concrete vervolgafspraak.\n\n"
                "Vooraf: bereid een pitch van 30 seconden, drie vaardigheden en drie "
                "vragen per interessant challenge voor. Tijdens het event: kies maximaal "
                "twee challenges, benoem uw bijdrage en bespreek rollen en vervolgactie. "
                "Na afloop: bevestig dezelfde dag uw rol en eerste stap aan het team."
            )
        return (
            "Pre-Hackathon OneGov #2 preparation plan\n\n"
            "Prepare a 30-second introduction, three contribution skills and three "
            "challenge questions. During the event, focus on up to two challenges, "
            "state your contribution and agree roles and a next step. Afterward, confirm "
            "your first contribution and the next meeting with the selected team."
        )

    def _event_challenge_forecast(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Ориентировочный прогноз заданий для OneGov #2\n\n"
                "Я не могу знать закрытый список challenge до публикации организаторами. "
                "Но по названию OneGov и формату pre-hackathon наиболее вероятны не случайные задачи, "
                "а civic-tech задания вокруг государства, сервисов, данных и доверия.\n\n"
                "Вероятные направления\n\n"
                "1. Цифровые государственные услуги: как сделать понятнее путь гражданина через несколько ведомств.\n"
                "2. AI для публичного сектора: ассистенты, triage запросов, объяснимые решения, контроль качества ответов.\n"
                "3. Данные и интероперабельность: объединение разрозненных данных без потери приватности и контроля.\n"
                "4. Прозрачность и доверие: audit trail, explainability, проверяемые источники, понятные правила ответственности.\n"
                "5. Инклюзивный доступ: сервисы для мигрантов, пожилых, предпринимателей или людей с низкой цифровой грамотностью.\n"
                "6. Командная координация: как быстро собрать роль, процесс, прототип и демонстрацию результата.\n\n"
                "Что подготовить заранее\n\n"
                "1. Один короткий кейс: какую проблему гражданина или организации вы хотите упростить.\n"
                "2. Карточку навыков: AI/governance, research, UX, backend, data, policy, presentation.\n"
                "3. Три вопроса к каждому challenge: кто пользователь, какой результат измеряется, какие ограничения по данным/закону.\n"
                "4. Мини-шаблон решения: проблема -> пользователь -> данные -> риск -> прототип -> как доказать пользу.\n\n"
                "Мой прогноз по лучшей позиции для вас: заходить не как просто участник, а как человек, который умеет "
                "соединять AI, governance и понятный пользовательский сценарий. Это даст ценность почти в любом OneGov challenge.\n\n"
                "Следующий практический шаг: пришлите ваши 3 навыка и язык участия, и я соберу вам короткий pitch "
                "под наиболее вероятные задания хакатона."
            )
        if context.language == "nl":
            return (
                "Voorlopige challenge-voorspelling voor OneGov #2\n\n"
                "Ik ken de gesloten challenge-lijst niet, maar verwacht civic-tech opdrachten rond "
                "digitale publieke dienstverlening, AI in de overheid, data-interoperabiliteit, "
                "transparantie, inclusieve toegang en teamcoordinatie. Bereid een korte pitch, "
                "uw drie vaardigheden en drie vragen per challenge voor: gebruiker, meetbaar resultaat "
                "en data/juridische beperkingen."
            )
        return (
            "Provisional challenge forecast for OneGov #2\n\n"
            "I cannot know the closed challenge list before organizers publish it. The likely areas are "
            "digital public services, AI for government, data interoperability, transparency and trust, "
            "inclusive access, and rapid team coordination. Prepare a short pitch, three contribution "
            "skills, and questions about user, measurable outcome, and data/legal constraints."
        )

    def _strategic_positioning(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Аудит качества ответа\n\n"
                "Предыдущий ответ был ошибкой runtime: запрос про позиционирование ASTREB TESTBOX "
                "не должен уходить в общий intake. Это не ваша ошибка. Системе не хватало явного "
                "навыка стратегического позиционирования и правила: если контекст неполный, сначала "
                "дать рабочую гипотезу и задать уточняющие вопросы.\n\n"
                "Корректирующее действие\n\n"
                "Позиционировать ASTREB TESTBOX лучше не как чатбот и не как демо, а как:\n\n"
                "ASTREB TESTBOX - governance and quality runtime for AI-assisted public-sector and operational workflows.\n\n"
                "Короткая русская формула:\n\n"
                "ASTREB TESTBOX - среда управления качеством и governance для AI-процессов: она показывает, "
                "как AI принимает решения, где возникают отклонения, какие вмешательства применяются и чему система учится.\n\n"
                "Что важно подчеркнуть\n\n"
                "1. Не чатбот: TESTBOX не просто отвечает, а наблюдает процесс.\n"
                "2. Не dashboard: он не только показывает метрики, а фиксирует отклонения и вмешательства.\n"
                "3. Не автономный агент: human authority остается границей для approvals, сроков, официальных действий и внешней отправки.\n"
                "4. Не proof-of-concept без следа: каждый существенный шаг пишет audit и learning record.\n"
                "5. Ценность для организаций: меньше слепой автоматизации, больше управляемого качества, объяснимости и ответственности.\n\n"
                "Рекомендуемая внешняя формула\n\n"
                "Controlled AI Governance Runtime for Quality, Auditability and Continuous Improvement.\n\n"
                "Для Нидерландов / public sector можно мягче:\n\n"
                "A controlled environment for testing, governing and improving AI-assisted administrative processes.\n\n"
                "Предупреждающее действие\n\n"
                "В таких вопросах TESTBOX должен всегда уточнять контекст, если его не хватает. Поэтому дальше я бы задал 4 вопроса:\n\n"
                "1. Для кого позиционируем: инвесторы, муниципалитеты, госорганизации, партнеры или хакатон-жюри?\n"
                "2. Что показываем первым: governance, QMS, audit, AI Cabinet, ASTI или public-sector workflow?\n"
                "3. Формат нужен какой: one-liner, pitch на 30 секунд, сайт, презентация или demo script?\n"
                "4. Язык и рынок: русский, английский, нидерландский; Европа, Нидерланды или международно?\n\n"
                "Мой первичный выбор: для запуска позиционировать как QMS/governance runtime, а не как AI assistant. "
                "Это сильнее, взрослее и точнее отличает ASTREB TESTBOX от обычных AI-инструментов."
            )
        return (
            "Quality audit: the previous response was a runtime miss, not a user error. "
            "ASTREB TESTBOX should be positioned as a governance and quality runtime, not as a chatbot or demo. "
            "Suggested line: Controlled AI Governance Runtime for Quality, Auditability and Continuous Improvement. "
            "Clarifying questions: audience, first proof point, format, language and market."
        )

    def _situation_intake(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Хорошо, разберём ситуацию. Напишите, что произошло, где, когда, "
                "кто участвует и какого результата вы хотите. Для регулируемой темы "
                "я отдельно проверю юрисдикцию, источники и риск."
            )
        return "Describe what happened, where, when, who is involved, and what outcome you need."

    def _general(self, context: AnswerContext) -> str:
        if context.language == "ru":
            return (
                "Я получил ваш запрос. Напишите, какой результат вам нужен: объяснение, "
                "план действий, проверка документа, подготовка письма или разбор ситуации.\n\n"
                "Если вопрос связан с законом, деньгами, статусом пребывания, работой, "
                "ДТП или компенсацией, укажите страну и основные факты. Тогда я проверю "
                "тему по доступным официальным источникам и покажу безопасный следующий шаг."
            )
        if context.language == "nl":
            return (
                "Ik heb uw vraag ontvangen. Geef aan of u uitleg, een stappenplan, "
                "documentcontrole of een brief nodig heeft."
            )
        return (
            "I received your request. Tell me whether you need an explanation, action "
            "plan, document review, draft letter, or situation assessment."
        )

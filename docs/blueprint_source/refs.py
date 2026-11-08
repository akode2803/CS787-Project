"""Bibliography. Metadata was fetched from the cited pages on 2026-10-28 unless marked with a dagger."""
from pdfkit import link, register_refs

A = "arXiv:"

def arx(i):
    return link(f"https://arxiv.org/abs/{i}", f"arXiv:{i}")

ITEMS = [
    # ---- base paper and artifacts
    ("zou", f"<b>BASE PAPER.</b> H. P. Zou, C. Miao, W.-C. Huang, Y. Chen, Y. Zhou, H. Zhang, Y. Wu, L. Fang, Z. Gu, Z. Zhang, K. Zheng, F. Wang, Y. Nian, S. Li, W. Fan, L. He, W. Zhang, X. Liu, P. S. Yu. "
            f"<i>When Users Change Their Mind: Evaluating Interruptible Agents in Long-Horizon Web Navigation.</i> {arx('2604.00892')}, submitted 1 Apr 2026 (v1; PDF header reads “Preprint. Under review.”). "
            f"PDF: {link('https://arxiv.org/pdf/2604.00892')}"),
    ("ib", "<b>BASE ARTIFACT.</b> InterruptBench code and data. " + link("https://github.com/HenryPengZou/InterruptBench") +
           " (we inspected commit 17da111, dated 2026-07-08)."),
    # ---- closest related work
    ("ivb", "<b>CLOSEST.</b> J. Lee, S. Bae, J.-S. Lee, Y. Choi, J.-H. Lee. <i>InterventionBench: Can LLM Agents Adapt to Mid-task User Interventions?</i> "
            "Findings of ACL: EMNLP 2026, pp. 14646–14666. " + link("https://aclanthology.org/2026.findings-emnlp.698/") + "; code/data: " + link("https://github.com/jhn25/InterventionBench")),
    ("task", "<b>CLOSEST.</b> C. Zhang, W. Kweon, J. Han. <i>How Strongly Should Task State Influence an LLM Agent?</i> " + arx("2609.25686") + ", 22 Sep 2026."),
    ("evolve", "<b>CLOSEST.</b> J. Tack, P. Laban, J. Neville. <i>LLMs Get Lost in Evolving User Intent.</i> " + arx("2607.20734") + ", 22 Jul 2026."),
    ("sweshift", "V. S.-J. Huang, R. Li, Z. Yin, K. Mao, Y. Zhao, X. Wang, Y. Yin, L. Luo, R. Zhang, H. Li. <i>SWE-Shift: Evaluating Coding Agents in Evolving Workspaces.</i> " + arx("2610.32196") + ", 23 Oct 2026."),
    ("featureloop", "J. Feng, A. Wu, C. Gao, Y. Wang, S. Lu, Z. Hu. <i>FeatureLoop: Benchmarking Coding Agents under Evolving Requirements.</i> " + arx("2610.35488") + ", 26 Oct 2026."),
    ("lrm", "T.-H. Wu, M. Miroyan, D. M. Chan, T. Darrell, N. Norouzi, J. E. Gonzalez. <i>Are Large Reasoning Models Interruptible?</i> " + arx("2510.11713") + ", Oct 2025 (several revisions). † Metadata from search-result summaries."),
    ("lost", "P. Laban, H. Hayashi, Y. Zhou, J. Neville. <i>LLMs Get Lost In Multi-Turn Conversation.</i> " + arx("2505.06120") + ", May 2025. † Metadata from search-result summaries."),
    ("contbench", "A. Gulati. <i>ContinuityBench: A Framework and Taxonomy for Evaluating Agent Recovery from Interrupted State.</i> Poster, ICML 2026 workshop “Combining Theory and Benchmarks”. " + link("https://icml.cc/virtual/2026/68364")),
    ("isp", "W. Hua, M. Wan, S. Vadrevu, R. Nadel, Y. Zhang, C. Wang. <i>Interactive Speculative Planning: Enhance Agent Efficiency through Co-design of System and User Interface.</i> " + arx("2410.00079") + ", Sep 2024."),
    ("ihbench", "A. Salimi, W. Ma, Y. Tang, D. Shen, M. Li, A. Smola. <i>IHBench: Evaluating Post-Interruption Recovery in Voice Agents with Structured Workflows.</i> " + arx("2606.19595") + ", 17 Jun 2026."),
    ("pifr", "Z. Liu, L. Cheng, Y. Liu, S. Tang, Y. Wang, Z. Zhong. <i>Preemptive Instruction Following with Resumption.</i> " + arx("2610.35576") + ", 26 Oct 2026 (embodied navigation; adjacent)."),
    # ---- planning, repair, state
    ("atg", "Y. Zhang, S. Chen, Z. Huang, H. Cui, K. Ji, Z. Wang. <i>Atomic Task Graph: A Unified Framework for Agentic Planning and Execution.</i> " + arx("2607.01942") + ", 2 Jul 2026."),
    ("lineage", "J. Rosen, S. Rosen. <i>From Agent Loops to Deterministic Graphs: Execution Lineage for Reproducible AI-Native Work.</i> " + arx("2605.06365") + ", 7 May 2026."),
    ("saga", "E. Y. Chang, L. Geng. <i>SagaLLM: Context Management, Validation, and Transaction Guarantees for Multi-Agent LLM Planning.</i> " + arx("2503.11951") + ", Mar 2025 (also listed in PVLDB vol. 18†)."),
    ("fox", "M. Fox, A. Gerevini, D. Long, I. Serina. <i>Plan stability: replanning versus plan repair.</i> ICAPS 2006. " + link("https://strathprints.strath.ac.uk/2776/") + " † Metadata from search-result summaries."),
    ("adaplanner", "H. Sun, Y. Zhuang, L. Kong, B. Dai, C. Zhang. <i>AdaPlanner: Adaptive Planning from Feedback with Language Models.</i> " + arx("2305.16653") + ", May 2023."),
    ("reflexion", "N. Shinn, F. Cassano, E. Berman, A. Gopinath, K. Narasimhan, S. Yao. <i>Reflexion: Language Agents with Verbal Reinforcement Learning.</i> " + arx("2303.11366") + ", Mar 2023."),
    ("react", "S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, Y. Cao. <i>ReAct: Synergizing Reasoning and Acting in Language Models.</i> " + arx("2210.03629") + ", Oct 2022 (ICLR)."),
    ("adapt", "A. Prasad, A. Koller, M. Hartmann, P. Clark, A. Sabharwal, M. Bansal, T. Khot. <i>ADaPT: As-Needed Decomposition and Planning with Language Models.</i> " + arx("2311.05772") + ", Nov 2023 (Findings of NAACL 2024)."),
    # ---- human-agent systems
    ("cogym", "Y. Shao, V. Samuel, Y. Jiang, J. Yang, D. Yang. <i>Collaborative Gym: A Framework for Enabling and Evaluating Human-Agent Collaboration.</i> " + arx("2412.15701") + ", Dec 2024 (ICLR 2026)."),
    ("magui", "H. Mozannar et al. <i>Magentic-UI: Towards Human-in-the-loop Agentic Systems.</i> " + arx("2507.22358") + ", 30 Jul 2025. † Only first author and abstract-level details verified."),
    # ---- environments and benchmarks
    ("webarena", "S. Zhou, F. F. Xu, H. Zhu, X. Zhou, R. Lo, A. Sridhar, X. Cheng, T. Ou, Y. Bisk, D. Fried, U. Alon, G. Neubig. <i>WebArena: A Realistic Web Environment for Building Autonomous Agents.</i> " + arx("2307.13854") + ", Jul 2023 (ICLR 2024)."),
    ("vwa", "J. Y. Koh, R. Lo, L. Jang, V. Duvvur, M. C. Lim, P.-Y. Huang, G. Neubig, S. Zhou, R. Salakhutdinov, D. Fried. <i>VisualWebArena: Evaluating Multimodal Agents on Realistic Visual Web Tasks.</i> " + arx("2401.13649") + ", Jan 2024 (ACL 2024)."),
    ("vab", "X. Liu, T. Zhang, Y. Gu, I. L. Iong, Y. Xu, et al. (30 authors). <i>VisualAgentBench: Towards Large Multimodal Models as Visual Foundation Agents.</i> " + arx("2408.06327") + ", Aug 2024. (Source of the WebArena-Lite subset, per the InterruptBench Eval README.)"),
    ("war1", "Z. Wei, W. Yao, Y. Liu, W. Zhang, Q. Lu, L. Qiu, C. Yu, P. Xu, C. Zhang, B. Yin, H. Yun, L. Li. <i>WebAgent-R1: Training Web Agents via End-to-End Multi-Turn Reinforcement Learning.</i> " + arx("2505.16421") + ", May 2025 (EMNLP 2025)."),
    ("taubench", "S. Yao, N. Shinn, P. Razavi, K. Narasimhan. <i>τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.</i> " + arx("2406.12045") + ", Jun 2024."),
    ("tau2", "V. Barres, H. Dong, S. Ray, X. Si, K. Narasimhan. <i>τ²-Bench: Evaluating Conversational Agents in a Dual-Control Environment.</i> " + arx("2506.07982") + ", Jun 2025."),
    # ---- harness documentation
    ("cc_int", "Anthropic. <i>Claude Code documentation — Interactive mode</i> (sections on Esc, Ctrl+Enter, “Queue messages while Claude works”). " + link("https://code.claude.com/docs/en/interactive-mode") + ". Accessed 2026-10-28."),
    ("cc_ckpt", "Anthropic. <i>Claude Code documentation — Checkpointing.</i> " + link("https://code.claude.com/docs/en/checkpointing") + ". Accessed 2026-10-28."),
    ("oa_steer", "OpenAI. <i>Mid-turn steering (Responses API guide).</i> " + link("https://developers.openai.com/api/docs/guides/steering") + ". Accessed 2026-10-28."),
    ("codex", "OpenAI. <i>Codex</i> repository (Apache-2.0), shallow clone at commit 154e873 (2026-10-28): " + link("https://github.com/openai/codex") +
              "; Python SDK reference <font face='DVM'>sdk/python/docs/api-reference.md</font>; protocol type <font face='DVM'>TurnSteerParams</font> in <font face='DVM'>codex-rs/app-server-protocol</font>."),
    ("codex_docs", "OpenAI. <i>Codex CLI</i> and <i>Developer commands</i> documentation. " + link("https://learn.chatgpt.com/docs/codex/cli") + " ; " + link("https://learn.chatgpt.com/docs/developer-commands") + ". Accessed 2026-10-28."),
    ("wa_docker", "WebArena authors. <i>environment_docker</i> README (AMI and map-backend notes). " + link("https://github.com/web-arena-x/webarena/tree/main/environment_docker") + ". Accessed 2026-10-28."),
]

register_refs(ITEMS)

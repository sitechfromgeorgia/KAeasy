# Technology & Artificial Intelligence Glossary

This glossary standardizes 150+ technology, artificial intelligence, machine learning, and cloud architecture terms in published Georgian text.

### Usage & Style Guidelines

1. **First mention convention**:
   - Spell out general technical concepts in natural Georgian on first mention, followed by the Latin acronym in parentheses if helpful:
     - `ხელოვნური ინტელექტი (AI)` → subsequent mentions as `AI`
     - `დიდი ენობრივი მოდელი (LLM)` → subsequent mentions as `LLM`
     - `გრაფიკული პროცესორი (GPU)` → subsequent mentions as `GPU`
2. **Latin stays Latin for proper nouns**:
   - Keep proprietary brand and model names in original Latin: `ChatGPT`, `Claude`, `Gemini`, `Llama`, `DeepSeek`, `PyTorch`, `TensorFlow`.
   - Never transcribe into Georgian (`ჩატჯიპიტი`, `ჯემინაი`).
3. **Case endings after hyphen**:
   - When affixing Georgian grammatical cases to Latin acronyms or names, use a hyphen: `AI-მ`, `AI-ს`, `GPU-ები`, `LLM-ის`.
   - Never write `AI-ები` for AI models — write `AI მოდელები`.
4. **Compound terms**:
   - Avoid awkward calques: e.g. `open source` is `ღია კოდის` or `ღია კოდის მქონე` (not `ღია წყარო`).
   - Words like `კიბერუსაფრთხოება`, `კიბერშეტევა`, `ჩატბოტი` are written as a single compound word without spaces or hyphens.

## Standard Terminology Table

| Latin / English | Preferred Georgian | Avoid (Incorrect / Russianism) | Note |
|---|---|---|---|
| model | **მოდელი** | `მოდელკა` | Core machine learning or statistical model. |
| fine-tuning | **ზუსტი მორგება** | `ფაინტუნინგი` | Adapting a pre-trained model on specialized data. Technical jargon 'ფაინ-ტიუნინგი' is also used. |
| inference | **ინფერენსი** | — | Executing a trained model. Also expressed as 'მოდელის გაშვება' or 'დასკვნის გამოტანა'. |
| prompt | **პრომპტი** | `პრომტი` | Input instruction or query given to a generative model. Always spelled with p-t (პტ). |
| token | **ტოკენი** | — | Sub-word or text fragment in NLP processing. |
| open source | **ღია კოდის** | `ოპენსორსი`, `ღია წყარო` | Software or model with publicly accessible source code: 'ღია კოდის მქონე'. |
| chip | **ჩიპი** | — | Integrated circuit or semiconductor microchip. Synonym: მიკროსქემა. |
| cloud / cloud service | **ღრუბლოვანი სერვისი** | `ღრუბელი` | Cloud infrastructure. Do not use bare 'ღრუბელი' without technical context. |
| artificial intelligence (AI) | **ხელოვნური ინტელექტი** | — | First mention in full: 'ხელოვნური ინტელექტი (AI)', subsequent mentions as 'AI'. |
| machine learning (ML) | **მანქანური სწავლება** | `მანქანური დასწავლა`, `მაშინ ლერნინგი` | Field of study giving computers ability to learn without explicit programming. |
| deep learning (DL) | **ღრმა სწავლება** | `ღრმა დასწავლა`, `დიპ ლერნინგი` | Subset of ML based on multi-layered neural networks. |
| neural network | **ნეირონული ქსელი** | `ნეიროქსელი` | Computational system modeled on biological neural networks. |
| large language model (LLM) | **დიდი ენობრივი მოდელი** | `დიდი ენის მოდელი` | Acronym LLM may follow in parentheses on first mention. |
| small language model (SLM) | **მცირე ენობრივი მოდელი** | — | Resource-efficient language model. |
| foundation model | **საბაზისო მოდელი** | — | Broadly trained model adapted to various downstream tasks. |
| frontier model | **მოწინავე მოდელი** | — | State-of-the-art model at the boundary of AI capabilities. |
| reasoning model | **მსჯელობის მოდელი** | — | Model trained specifically for step-by-step logical reasoning. |
| training | **მოდელის წვრთნა** | `ტრენინგი` | Computational optimization of parameters on training data. Also 'სწავლება'. |
| pre-training | **წინასწარი წვრთნა** | — | Initial training phase on large unannotated corpora. |
| post-training | **შემდგომი წვრთნა** | — | Post-pretraining phase including alignment, SFT, and RLHF. |
| weights | **წონები** | — | Learned internal parameters of neural network layers. |
| parameters | **პარამეტრები** | — | Configurable or learned variables in a mathematical model. |
| embeddings | **ვექტორული ჩანერგვა** | — | Vector representation of semantic tokens. Plural: 'ემბედინგები'. |
| vector database | **ვექტორული მონაცემთა ბაზა** | — | Specialized database indexing high-dimensional embeddings. |
| retrieval-augmented generation (RAG) | **ძიებით გამდიდრებული გენერაცია** | — | First mention in full; acronym 'RAG' used subsequently. |
| hallucination | **ჰალუცინაცია** | — | Plausible but ungrounded or factually incorrect generation by LLM. |
| context window | **კონტექსტის ფანჯარა** | — | Maximum token capacity a model can process in one call. |
| context length | **კონტექსტის სიგრძე** | — | Token count in context window. |
| temperature | **ტემპერატურა** | — | Hyperparameter controlling randomness of token selection. |
| latency | **დაყოვნება** | `ლატენტურობა` | Time taken from request dispatch to response arrival. |
| throughput | **გამტარუნარიანობა** | — | Volume of tokens or requests processed per second. |
| benchmark | **ბენჩმარკი** | — | Standardized evaluation test suite. Synonym: საორიენტაციო ტესტი. |
| dataset | **მონაცემთა ნაკრები** | `დატასეტი` | Curated collection of training or testing data. |
| zero-shot learning | **ნულოვანი გადაცემით სწავლება** | — | Performing a task without task-specific training examples. Also 'zero-shot სწავლება'. |
| few-shot prompting | **რამდენიმე მაგალითით მითითება** | — | Supplying several demonstration exemplars inside the prompt. |
| one-shot learning | **ერთმაგალითიანი სწავლება** | — | Learning or prompting with exactly one demonstration. |
| reinforcement learning (RL) | **განმტკიცებითი სწავლება** | `რეინფორსმენტ ლერნინგი` | Agent learning optimal policies through environmental rewards and penalties. |
| RLHF | **განმტკიცებითი სწავლება ადამიანის უკუკავშირით** | — | Reinforcement learning from human feedback. |
| direct preference optimization (DPO) | **პირდაპირი პრეფერენციული ოპტიმიზაცია** | — | Alignment without training a separate reward model. |
| transformer | **ტრანსფორმერი** | — | Neural network architecture based on self-attention mechanisms. |
| attention mechanism | **ყურადღების მექანიზმი** | — | Mathematical mechanism weighing dynamic relevance of tokens. |
| self-attention | **თვითყურადღება** | — | Attention applied within the same sequence. |
| cross-attention | **ჯვარედინი ყურადღება** | — | Attention mapping between two distinct sequences (e.g. text to image). |
| quantization | **კვანტიზაცია** | — | Reducing numerical precision of model weights (e.g. FP16 to INT8/INT4). |
| pruning | **გასხვლა** | — | Removing redundant weights or attention heads from a neural net. Also 'შეკვეცა'. |
| model distillation | **მოდელის დისტილაცია** | — | Training a compact student model on outputs of a larger teacher model. |
| multimodal | **მულტიმოდალური** | `მრავალმოდალური` | Processing multiple sensory modes (text, audio, vision). |
| diffusion model | **დიფუზიური მოდელი** | — | Generative model based on iterative denoising processes. |
| generative AI | **გენერაციული ხელოვნური ინტელექტი** | — | AI synthesizing novel content (text, audio, image, code). |
| computer vision | **კომპიუტერული ხედვა** | — | AI processing and understanding visual imagery. |
| natural language processing (NLP) | **ბუნებრივი ენის დამუშავება** | `ნატურალური ენის დამუშავება` | 'ნატურალური ენის დამუშავება' is a Russianism. |
| natural language understanding (NLU) | **ბუნებრივი ენის გააზრება** | — | Subfield of NLP focusing on machine comprehension. |
| natural language generation (NLG) | **ბუნებრივი ენის გენერაცია** | — | Synthesizing coherent human-readable text. |
| speech-to-text (STT) | **მეტყველების ტექსტად გარდაქმნა** | — | Automated speech recognition (ASR). |
| text-to-speech (TTS) | **ტექსტის გახმოვანება** | — | Neural speech synthesis. Also 'მეტყველებად გარდაქმნა'. |
| text-to-image (T2I) | **ტექსტის გამოსახულებად გარდაქმნა** | — | Synthesizing graphics from natural language prompts. |
| text-to-video (T2V) | **ტექსტის ვიდეოდ გარდაქმნა** | — | Synthesizing video clips from prompt instructions. |
| image-to-video (I2V) | **გამოსახულების ვიდეოდ გარდაქმნა** | — | Animating static input images into coherent video sequences. |
| autonomous agent | **ავტონომიური აგენტი** | — | Entity perceiving environment and taking actions to reach assigned goals. |
| multi-agent system | **მრავალაგენტიანი სისტემა** | — | Orchestration of collaborative or specialized autonomous agents. |
| chain-of-thought (CoT) | **მსჯელობის ჯაჭვი** | — | Decomposing complex queries into intermediate reasoning steps. |
| tree-of-thoughts (ToT) | **აზრთა ხე** | — | Exploration of multiple branching reasoning paths. |
| overfitting | **გადამეტებული მორგება** | `გადამეტებული გადამზადება`, `ოვერფიტინგი` | Model fits training noise and generalizes poorly to unseen data. |
| underfitting | **არასაკმარისი მორგება** | — | Model fails to capture underlying patterns in training data. |
| bias | **მიკერძოებულობა** | `ბიასი` | Systematic skew or prejudice in training data and model outputs. |
| variance | **დისპერსია** | — | Sensitivity of model predictions to fluctuations in training sets. |
| alignment | **თანხვედრა** | — | Ensuring model behaviors align with human intent and ethical values. Also 'მორგება'. |
| safety guardrails | **უსაფრთხოების ზღუდეები** | — | Programmatic filters and checks preventing hazardous outputs. |
| chatbot | **ჩატბოტი** | `ჩატ ბოტი` | One word in Georgian: ჩატბოტი. |
| pipeline | **დამუშავების ეტაპები** | — | Sequence of connected data processing stages. In technical code: 'პაიპლაინი'. |
| frontend | **ფრონტენდი** | `წინა მხარე` | Client-side user presentation layer. |
| backend | **ბექენდი** | `უკანა მხარე` | Server-side business logic and database persistence layer. |
| API | **აპლიკაციის პროგრამული ინტერფეისი** | — | Contract for inter-program communication. Common acronym: 'API'. |
| framework | **ფრეიმვორკი** | — | Standardized software platform or skeleton architecture. |
| repository | **რეპოზიტორია** | — | Storage location for software packages or source code. Synonym: საცავი. |
| open weights | **ღია წონები** | — | Models releasing neural network weights publicly. |
| closed source | **დახურული კოდის** | — | Proprietary software with non-public source code. |
| proprietary | **საკუთრებითი** | — | Commercial technology owned exclusively by a single enterprise. |
| edge computing | **პერიფერიული გამოთვლები** | — | Computing performed locally on client devices rather than centralized clouds. |
| caching | **ქეშირება** | `დაქეშვა` | Storing copies of data in rapid transient storage. |
| hardware accelerator | **აპარატურული ამაჩქარებელი** | — | Specialized silicon speeding up numerical workloads. |
| GPU | **გრაფიკული პროცესორი** | — | Graphics processing unit. Abbreviation 'GPU' hyphenated in Georgian (GPU-ები). |
| TPU | **ტენზორული პროცესორი** | — | Google-designed ASIC accelerator for tensor calculations. |
| NPU | **ნეირონული პროცესორი** | — | Neural processing unit designed for on-device inference. |
| CPU | **ცენტრალური პროცესორი** | — | Main execution engine of a computer. |
| memory bandwidth | **მეხსიერების გამტარუნარიანობა** | — | Rate at which data can be read from or stored into semiconductor memory. |
| compute cluster | **გამოთვლითი კლასტერი** | — | Interconnected group of compute servers acting as a single resource. |
| data center | **მონაცემთა ცენტრი** | — | Facility housing networked computer servers and enterprise storage systems. |
| server | **სერვერი** | — | Computer program or device providing service to clients. |
| database | **მონაცემთა ბაზა** | — | Structured set of data held in a computer. |
| software | **პროგრამული უზრუნველყოფა** | — | Programs and operating information used by a computer. |
| hardware | **აპარატურული უზრუნველყოფა** | — | Physical components of a computer system. |
| firmware | **მიკროპროგრამული უზრუნველყოფა** | — | Permanent software programmed into read-only memory. |
| algorithm | **ალგორითმი** | — | Step-by-step procedure for solving a computational problem. |
| loss function | **დანაკარგის ფუნქცია** | — | Mathematical objective function measuring model error during training. |
| gradient descent | **გრადიენტული დაშვება** | — | First-order iterative optimization algorithm for finding a local minimum. |
| backpropagation | **უკუგავრცელება** | — | Backward pass algorithm calculating gradient of loss function with respect to weights. |
| learning rate | **სწავლის სიჩქარე** | — | Step size hyperparameter in gradient descent. |
| batch size | **პაკეტის ზომა** | — | Number of training samples evaluated in one forward/backward pass. |
| epoch | **ეპოქა** | — | One complete pass through the entirety of a training dataset. |
| checkpoint | **საკონტროლო წერტილი** | — | Saved snapshot of model weights during training. |
| prompt engineering | **პრომპტ-ინჟინერია** | `პრომტ ინჟინერია` | Structuring and optimizing prompt instructions for generative models. |
| system prompt | **სისტემური პრომპტი** | `სისტემური პრომტი` | High-priority instructions setting persona and boundaries for an LLM. |
| user prompt | **მომხმარებლის პრომპტი** | `იუზერ პრომპტი` | Turn query or instruction issued by the end-user. |
| assistant response | **ასისტენტის პასუხი** | — | Generation delivered back by conversational agent. |
| context injection | **კონტექსტის შეყვანა** | — | Passing dynamic grounding data into the prompt payload. |
| grounding | **ფაქტობრივი დაფუძნება** | — | Anchoring model outputs in verifiable retrieval sources. Technical: გრაუნდინგი. |
| semantic search | **სემანტიკური ძიება** | — | Searching by conceptual meaning rather than literal keyword matches. |
| similarity search | **მსგავსების მიხედვით ძიება** | — | Nearest neighbor query in high-dimensional vector spaces. |
| cosine similarity | **კოსინუსური მსგავსება** | — | Metric measuring cosine of the angle between two non-zero vectors. |
| vector space | **ვექტორული სივრცე** | — | Mathematical space in which vectors can be combined and scaled. |
| dimension | **განზომილება** | — | Vector dimensionality representing features. |
| synthetic data | **სინთეზური მონაცემები** | — | Artificially generated training data produced by computer simulations or AI. |
| data labeling | **მონაცემთა მარკირება** | — | Attaching ground truth labels to raw data. |
| annotation | **ანოტაცია** | — | Detailed semantic tagging of training samples. |
| supervised learning | **ზედამხედველობითი სწავლება** | — | ML paradigm using labeled input-output pairs. |
| unsupervised learning | **ზედამხედველობის გარეშე სწავლება** | — | ML paradigm finding inherent clusters and patterns without target labels. |
| self-supervised learning | **თვითზედამხედველობითი სწავლება** | — | Training where supervisory signals are derived directly from the unannotated data. |
| transfer learning | **ტრანსფერული სწავლება** | — | Applying knowledge acquired in one problem domain to a different one. |
| active learning | **აქტიური სწავლება** | — | Algorithm interactively querying human annotators for new labels. |
| prompt injection | **პრომპტის ინექცია** | `პრომტ ინექცია` | Adversarial exploit manipulating prompt instructions to bypass guardrails. |
| jailbreak | **დაცვის გარღვევა** | — | Bypassing safety alignment constraints in an LLM. Also 'ჯეილბრეიკი'. |
| adversarial attack | **შეტაკებითი შეტევა** | — | Deliberately crafting perturbed inputs designed to deceive an ML model. |
| watermarking | **ციფრული წყლის ნიშანი** | — | Embedding invisible cryptographic or statistical markers into generated media. |
| red teaming | **წითელი გუნდის შემოწმება** | — | Structured adversarial testing to uncover vulnerabilities. Also 'რედ-თიმინგი'. |
| evaluation | **შეფასება** | — | Assessing model accuracy, bias, and performance against benchmark standards. Also 'ევალუაცია'. |
| leaderboard | **ლიდერბორდი** | — | Comparative ranking board for models on specific benchmarks. Also 'რეიტინგის დაფა'. |
| PEFT | **პარამეტრულად ეფექტიანი ზუსტი მორგება** | — | Parameter-efficient fine-tuning. |
| LoRA | **დაბალი რანგის ადაპტაცია** | — | Low-rank adaptation: freezing weights and injecting trainable rank decomposition matrices. |
| mixture of experts (MoE) | **ექსპერტთა ნაზავი** | — | Sparse architecture routing tokens to specialized expert sub-networks. |
| top-k sampling | **top-k შერჩევა** | — | Restricting next-token sampling to the k highest-probability candidates. |
| top-p sampling (nucleus) | **top-p შერჩევა** | — | Restricting sampling to smallest candidate pool whose cumulative probability exceeds p. |
| greedy decoding | **ხარბი დეკოდირება** | — | Deterministically selecting token with highest probability at each step. |
| beam search | **სხივური ძიება** | — | Heuristic search algorithm maintaining a predetermined number of best candidate paths. |
| autoencoder | **ავტოენკოდერი** | — | Neural network trained to compress and reconstruct its own inputs. |
| encoder-decoder | **ენკოდერ-დეკოდერი** | — | Sequence-to-sequence model structure (e.g. original T5). |
| decoder-only | **მხოლოდ დეკოდერი** | — | Autoregressive architecture characteristic of modern LLMs (e.g. GPT, LLaMA). |
| encoder-only | **მხოლოდ ენკოდერი** | — | Bidirectional representation architecture (e.g. BERT). |
| state space model (SSM) | **მდგომარეობათა სივრცის მოდელი** | — | Sub-quadratic sequential processing architecture (e.g. Mamba). |
| recurrent neural network (RNN) | **რეკურენტული ნეირონული ქსელი** | — | Neural network containing internal recurrence loops. |
| convolutional neural network (CNN) | **კონვოლუციური ნეირონული ქსელი** | — | Grid-processing neural network using spatial convolution kernels. |
| cybersecurity | **კიბერუსაფრთხოება** | `კიბერ უსაფრთხოება` | Protection of computer systems from malicious digital attacks. Written as one word. |
| cyberattack | **კიბერშეტევა** | `კიბერ შეტევა` | Malicious attempt to damage or disrupt a computer network. Written as one word. |
| phishing | **ფიშინგი** | — | Deceptive attempt to obtain sensitive credentials. |
| malware | **მავნე პროგრამა** | — | Hostile or intrusive software designed to harm computers. |
| ransomware | **გამომძალველი პროგრამა** | — | Extortion software encrypting victim files until payment is delivered. |
| vulnerability | **მოწყვლადობა** | — | Flaw or weakness in software logic or design. Synonym: ხარვეზი. |
| zero-day exploit | **ნულოვანი დღის ექსპლოიტი** | — | Cyberattack targeting an undisclosed software flaw unknown to the vendor. |
| encryption | **დაშიფვრა** | `შიფრაცია` | 'შიფრაცია' is a Russianism; correct Georgian is 'დაშიფვრა'. |
| decryption | **გაშიფვრა** | — | Reversing encryption to recover plaintext. |
| digital signature | **ციფრული ხელმოწერა** | — | Cryptographic authentication mechanism ensuring non-repudiation. |
| cloud provider | **ღრუბლოვანი პროვაიდერი** | — | Commercial entity offering hosted infrastructure (e.g. AWS, GCP, Azure). |
| serverless | **უსერვერო არქიტექტურა** | — | Event-driven execution model where server provisioning is handled transparently. |
| containerization | **კონტეინერიზაცია** | — | Encapsulating software dependencies into portable isolated runtimes (e.g. Docker). |
| microservices | **მიკროსერვისები** | — | Architectural approach decomposing apps into small, decoupled services. |

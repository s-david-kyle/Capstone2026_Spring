# Overview
Grok 3 is the third iteration of Grok. As with Grok 1 and Grok 2, Grok 3 is written in a combination of the [Rust and Python](https://www.techtarget.com/searchapparchitecture/tip/When-to-use-Rust-vs-Python) programming languages. While Grok 1 had some code available under the [open source](https://www.techtarget.com/whatis/definition/open-source) Apache 2.0 license, Grok 3 is not open source and has a proprietary license.

Among Grok 3's innovations is the expanded training infrastructure used to develop the model -- xAI's proprietary Colossus supercomputer cluster. According to xAI, that supercluster initially included more than 100,000 Nvidia Hopper GPUs, the most powerful GPU available for production deployments during Grok's training. The Colossus supercluster also employs Nvidia Spectrum-X [E](https://www.techtarget.com/searchnetworking/definition/Ethernet)[thernet](https://www.techtarget.com/searchnetworking/definition/Ethernet) for connectivity, enabling high-performance throughput while training the model.

There are two versions of Grok 3. The base version is simply known as Grok 3, while Grok 3 mini is a smaller, more cost-efficient model.
# DKG-LLM Impementation
The Grok 3 model extracts semantic information from unstructured medical texts (e.g., clinical reports, PubMed articles, patient records).
# See also
- [[DKG-LLM Framework]]
# Source
- https://x.ai/news/grok-3
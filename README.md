# Grammateus 
<pre>
    In ancient Greece the specific role responsible for documenting
    legal proceedings, similar to a scribe or notary, was called a 
    "grammateus" (γραμματεύς).
</pre>
Documenting interactions with Language Models requires several types of records, namely: a 'technical log' - the exact queries presented to the Model through the API and API responses; a 'conversation history' - the formatted messages and resposes that can be resent to a model, and, finally a human-readable 'record of conversation' which can be easily ingested back into the Python code querying the Model for a continuation of the conversation.

The first and secondtask are easily solvable with `jsonlines` library and `jl` format. It took me some time to realize that the best format for human-readable record is `YAML`.

There are two main reasons for that: YAML lets you drop double quotes and YAML permits comments which are absolutely necessary if you are systematically working on natural language interactions with Language Models.

In particular, the human-readable record of a conversation can look like this:
```yaml
- instruction: Be an Abstract Intellect.
- human: Let's talk about Human Nature.
- machine: Yes, let's do that, it's a complex topic...
```
If you want to preserve comments (this is what they call 'round-trip' compatibility) and more control over the format of 'emission'you can use the `ruamel.yaml` library and modify the yaml .

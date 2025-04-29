# Grammateus 
<pre>
    In ancient Greece the specific role responsible for documenting
    legal proceedings, similar to a scribe or notary, was called a 
    "grammateus" (γραμματεύς).
</pre>
Documenting interactions with Language Models requires several types of records, namely: a 'technical log' - the exact queries presented to the Model through the API and API responses; a 'conversation history' - the formatted messages and responses that can be re-sent back to the model (a local 'cache'); and, finally, a human-readable 'record of conversation' which can be easily ingested back into the Python code querying the Model and transformed for continuation of the conversation.

The first and second tasks are easily solvable with `jsonlines` library and `jl` format. It took me some time to realize that the best format for human-readable record is `YAML`.

There are two main reasons for that: YAML lets you drop double quotes, and YAML (unlike JSON)permits comments which are absolutely necessary if you are systematically working on natural language interactions with Language Models.

In particular, a human-readable record of conversation can look like this:
```yaml
- instruction: Be an Abstract Intellect.      # this is a comment
- Human: Let's talk about Human Nature.       # this is a comment
- machine: Yes, let's do that, it's a complex topic...
```

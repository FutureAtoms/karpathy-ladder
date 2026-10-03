# Self-attention: narration

**Message:** Each word becomes a blend of the values, weighted by how well its query matches each key.

**Voice:** Kokoro `am_michael` (calm American male), speed 1.0, made on this Mac with kokoro-onnx. Another good Kokoro voice for this style is `af_heart` (American female). To change the voice, edit `voice` in `source/script.json` and run `source/build.sh`.

**Length:** 118 words. The speech ends at 44.4 s. The video ends at 47.9 s, after a closing hold with the message on screen. These timings come from the build of 2026-10-03.

## Script

The source of truth is `source/script.json`. Each line below is one voice clip and one subtitle cue.

Scene 1, a sentence and the word bank:

- Self-attention lets every word borrow meaning from the words around it.
- Watch the word bank.

Scene 2, query, key and value:

- Three matrices, learned in training, give each word three vectors.
- A query asks what the word needs.
- A key says what it offers.
- A value holds what it shares.

Scene 3, the dot product:

- A dot product compares bank's query with each key.
- Arrows that point the same way give a high score.

Scene 4, scale and softmax:

- Then divide each score by the square root of the key size.
- Softmax turns the scores into weights that total one.

Scene 5, the weighted sum of the values:

- Scale each value by its weight.
- The sum is the new bank vector.
- River has the most weight, so bank leans toward the river meaning.

Scene 6, the formula:

- Every word does this at once, in one formula.

## Facts behind the script

- The formula is scaled dot-product attention from Vaswani et al., "Attention Is All You Need" (2017), section 3.2.1.
- The paper divides by the square root of d_k because large dot products push softmax into regions where the gradients are very small.
- In self-attention, the queries, keys and values all come from the same words, through learned matrices W_Q, W_K and W_V.
- The numbers on screen are a toy example in 2 dimensions, so d_k is 2. The base model in the paper uses d_k = 64.

## What the video leaves out

- Multi-head attention: a transformer runs several of these attention operations in parallel and joins the results.
- The causal mask: in a model that writes text, a word can only look at the words before it. In this sentence, "river" comes before "bank", so the example still holds.
- The output step: the model adds the attention result to the vector of the word. It does not replace the vector.

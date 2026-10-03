# Self-attention: scene plan

**Message:** Each word becomes a blend of the values, weighted by how well its query matches each key.

**Look:** dark background, light ink, LaTeX type. Yellow is the accent for bank (its query and its new vector). Blue is the contrast color for the keys and values of all words. The video has no burned-in captions. The subtitles are a soft track in the `.mp4` and a separate `.srt`.

**Times** come from the voice clips of the build of 2026-10-03 (`timings.json`). The scene code waits for the start of each sentence, so a new voice changes the times but keeps each visual on its words.

| # | Seconds | Narration (exact words) | On screen | Motion |
|---|---|---|---|---|
| 1 | 0.0 to 6.7 | "Self-attention lets every word borrow meaning from the words around it. Watch the word bank." | Title "Self-attention". The sentence "the muddy river bank" as 4 word boxes. | The title writes in. The boxes fade in from left to right. On "bank", its box turns yellow and arcs grow from bank to the other words. |
| 2 | 6.7 to 17.5 | "Three matrices, learned in training, give each word three vectors. A query asks what the word needs. A key says what it offers. A value holds what it shares." | The word boxes move to the top. A grid of arrows with a row for each vector and a column for each word. The formulas `q = W_Q x`, `k = W_K x` and `v = W_V x` label the rows. | The note "`W_Q, W_K, W_V`: learned in training" fades in, then the formulas write. On each of "query", "key" and "value", a row of small arrows grows. The query of bank is yellow, the other queries are grey. |
| 3 | 17.5 to 24.3 | "A dot product compares bank's query with each key. Arrows that point the same way give a high score." | A plane with the query of bank (yellow) and the 4 keys (blue), each labeled with its word. A table at the right shows `q_bank · k` for each word: 0.00, 1.40, 4.06, 1.68. | The query arrow and the key arrows fly from the grid into the plane and grow. Each key flashes as its score appears. On "same way", the river key gets thicker, a dashed line extends the query, and 4.06 turns yellow. |
| 4 | 24.3 to 31.8 | "Then divide each score by the square root of the key size. Softmax turns the scores into weights that total one." | The header changes to `q · k / √d_k`, with the note "key size `d_k = 2`". The scores become 0.00, 0.99, 2.87, 1.19. A softmax column of bars: 0.04, 0.11, 0.72, 0.13, and the line 0.04 + 0.11 + 0.72 + 0.13 = 1. | The old numbers fade up and out, the scaled numbers fade in. The bars grow from the left. The sum line writes in. |
| 5 | 31.8 to 40.9 | "Scale each value by its weight. The sum is the new bank vector. River has the most weight, so bank leans toward the river meaning." | The plane now shows the 4 value vectors (blue). Faint copies stay at full length. A yellow arrow "new bank" is the weighted sum. | The keys fade out and the values grow. Each value shrinks to its weight times its length. The scaled values join tip to tail, then the yellow sum arrow grows from the origin. On "river", a dashed line shows the river direction and the 0.72 bar turns yellow. |
| 6 | 40.9 to 47.9 | "Every word does this at once, in one formula." | The 4 word boxes with arcs from bank, line width set by the weights. The formula `Attention(Q, K, V) = softmax(QKᵀ / √d_k) V`. The message under it. | The plane and the table fade out. The boxes move to the center and the weighted arcs grow. The formula writes in. The message fades in and holds for 3 s. |

## Toy numbers

The numbers are a 2-dimensional toy, computed in `source/scene.py`, so that the dot product shows as alignment on a plane.

- Query of bank: (1.4, 0.7).
- Keys: the (-0.5, 1.0), muddy (1.2, -0.4), river (2.2, 1.4), bank (0.3, 1.8).
- Values: the (-0.8, 0.6), muddy (0.6, -1.0), river (2.0, 1.5), bank (-0.8, 1.2).
- Scores q · k: 0.00, 1.40, 4.06, 1.68. Divided by √2: 0.00, 0.99, 2.87, 1.19.
- Softmax weights: 0.04, 0.11, 0.72, 0.13. The rounded weights total 1.00. The script stops the build if they do not.
- New bank vector: approximately (1.36, 1.15), at 40 degrees. The river value (2.0, 1.5) is at 37 degrees, so the new vector points close to it.

## Source panels

These are the questions that the scenes answer, one for each panel of a spec sheet on the same subject.

- A, what self-attention does: each word takes meaning from the other words (scene 1).
- B, where the vectors come from: learned matrices give the query, key and value (scene 2).
- C, how a word picks its context: the dot product of the query with each key (scene 3).
- D, how scores become weights: the division by √d_k, then softmax (scene 4).
- E, what the word gets: the weighted sum of the values (scene 5).
- F, the whole operation: the matrix formula from Vaswani et al. 2017 (scene 6).

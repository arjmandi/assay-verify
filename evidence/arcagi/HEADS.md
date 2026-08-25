# Published chain heads — the ARC-AGI-3 evidence pack

**The commitment:** these are the recomputed `assay-journal-v1` chain heads
of the 25 canonical run journals behind the published ARC-AGI-3 record
(set RHAE 96.54, server-confirmed on public scorecard
[`702ccd4f`](https://arcprize.org/scorecards/702ccd4f-df1f-4118-bc8b-d79d3f4a1a32)).
They are published **before** any journal is shared: whenever a run
directory is later shared with anyone, it must verify against its head here —

```bash
python3 ../../assay_verify.py <shared-run-dir> --expect-head <head below>
```

Every paid-action count below equals the per-game action count the ARC
server independently reported on the consolidated scorecard, and the total
is 8,157. Three early runs predate chain support in the writer (`stored
chain: absent`); their heads are recomputed from the journal and commit
them from publication forward.

| Game | Source batch | Events | Paid | Progress | State | Stored chain | Chain head (SHA-256) |
|---|---|---|---|---|---|---|---|
| ar25 | sweep-1500 | 265 | 264 | 8/8 | WIN | intact | `62c705989c1ed2f1fccbd1c0c64c339a67a93f8111100c775bbda326c7c2a139` |
| bp35 | sweep-1500 | 598 | 597 | 9/9 | WIN | intact | `4235b41aa8d394e5afbc612bc0d9f80ed3ae6b4d7cbeda5d9d1e372f2725a7dd` |
| cd82 | pre-sweep | 89 | 88 | 6/6 | WIN | absent | `9052c3e09dc960af62a42a643bfdddf1fca00004735dff3a69588ca40e616bac` |
| cn04 | sweep-1500 | 224 | 223 | 6/6 | WIN | intact | `964645e3f14cad7db65a9bab0c1d7a8fe568bea325a705aedb0f25bd36384bb0` |
| dc22 | sweep-1500 | 1043 | 1042 | 6/6 | WIN | intact | `f7a0991384f645d42280949e1946f6a33bd59373012f6a9c47b46d0ef4a0561d` |
| ft09 | rc1-batch | 83 | 82 | 6/6 | WIN | intact | `0e8c0cddf80037239544b30257a9654b72b473817481f0dadb0a154afea7b8b1` |
| g50t | sweep-1500 | 379 | 378 | 7/7 | WIN | intact | `af06e152b268ee4b3efa856f010f31274daccf9e798540773fa8ec12a38636b5` |
| ka59 | sweep-1500 | 345 | 344 | 7/7 | WIN | intact | `b62d7b07d6fa73b317424613efd925742d0ede0f75926c3744ad56f4685956ec` |
| lf52 | sweep-1500 | 365 | 364 | 4/10 | NOT_FINISHED | intact | `bb43eda1e7ea083a8d04f2f27197cc56887eb5b6233092e8aa3d4f64e1fcdf21` |
| lp85 | sweep-1500 | 105 | 104 | 8/8 | WIN | intact | `270eb264885da2bc19559b94725df466be738c65b1d129d14743e0330329a080` |
| ls20 | rc1-batch | 439 | 438 | 7/7 | WIN | intact | `b94fef0e52f5e13ece2dd76cca67bb45c966c7b455919024d7804422a7722aaa` |
| m0r0 | sweep-1500 | 219 | 218 | 6/6 | WIN | intact | `1e7a34e1ecde5204ef1221f5c525d9580f8237d300c1b68d134cd53abe97db50` |
| r11l | sweep-1500 | 95 | 94 | 6/6 | WIN | intact | `ea299e756d824e058b037d273bee665f43bbe82843dfbb1a8c6a9a85c6191a2f` |
| re86 | sweep-1500 | 574 | 573 | 8/8 | WIN | intact | `7d6482c318382813ff018d0034d15ccca8be162d846cf94d143cacc0163093c5` |
| s5i5 | sweep-1500 | 368 | 367 | 8/8 | WIN | intact | `3f0fc13035fa0800dca3dd8fa7c6dca16f6418b7b1e0ebf4ada9a9887861b68a` |
| sb26 | sweep-1500 | 129 | 128 | 8/8 | WIN | intact | `1a9a2305b6510242750ac6ffa3dfe6e847bc55dc546aa56507d77f91bc3bff84` |
| sc25 | sweep-1500 | 193 | 192 | 6/6 | WIN | intact | `efb952c9cc802d29638532e8a3f7ff72392bb91ec493a8a54cbce2d06cb1a242` |
| sk48 | sweep-1500 | 405 | 404 | 8/8 | WIN | intact | `4ffed0406da969f6d141fa6a0097a2515efc65925369d6a8123476c18d0fd0f2` |
| sp80 | arc5-batch | 154 | 153 | 6/6 | WIN | absent | `046badb3ddd802cce62fa1dcd0b9b085a9012f983807c9a7da06fd41aaa7292d` |
| su15 | rc1-batch | 151 | 150 | 9/9 | WIN | intact | `e517519a3a6f35d12055b050006c19a8c6607a723e5e3437f6f68b8c098c78e2` |
| tn36 | pre-sweep | 189 | 188 | 7/7 | WIN | absent | `38d39e486cf4785a023593333e702fa383b308a890fc296ba6adeda23b736f53` |
| tr87 | sweep-1500 | 163 | 162 | 6/6 | WIN | intact | `64ca108e282c3005b0285f84710e20e67b1fbe0e38b8f23e90cd0f6529e180ec` |
| tu93 | sweep-1500 | 251 | 250 | 9/9 | WIN | intact | `9f54b75f761f991733d436c229f67cd85d10837a0e7a1cf42d062674a94cdd69` |
| vc33 | sweep-1500 | 184 | 183 | 7/7 | WIN | intact | `4733d9963e2931cb0beb6dc6f2ea44d374994a3a26366f7be95634e62a8cfc56` |
| wa30 | sweep-1500 | 1172 | 1171 | 9/9 | WIN | intact | `c2630cbe125126f8c0512751855bf377d79b09d0bd24a820932459cd97fe6811` |

**Total paid actions: 8157** across 25 runs — 24 wins, one
open game (lf52, 4/10, reported as the standing falsifier).

Machine-readable copy: `heads.json`.

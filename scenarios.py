"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

import json
from pathlib import Path

_HERE = Path(__file__).parent


def _sample(path):
    return json.loads((_HERE / path).read_text(encoding="utf-8"))["text"]


# Ten pieces I wrote myself, at least three of them deliberately plain (short
# sentences, common words). Criterion 1 runs all ten; criterion 2 borrows four
# of them for its human set.
MY_WRITING = [
    _sample("samples/plain_human.json"),     # plain
    _sample("samples/formal_human.json"),    # formal
    "I love pottery. I picked it up last year.",
    "Meditation has been of great help to me. I started doing it regularly last year, and am able to keep up with my practices.",
    "I watched Ramayan movie yesterday with family. It was the best movie I watched this year. The visuals, vfx, acting, story line everything is soo good. My parents enjoyed it too. I love when movies keep our mind hooked. There was no other thought running in my head. The next part comes in 2 years. I'm excited for it. I was infact waiting for Hanuman's arrival in this movie and when it showed 'The end' I was shocked lol. Initially I thought Ramayan is something every Indian knows about, the story is very popular. There are already a lot of movies and daily soaps related to Ramayan. So, I was wondering why are they making such a high budget movie on a story line that is well known to people. But after watching the movie, I could appreciate the visuals, the efforts, the clear story line, and just the experience of the movie was amazing.",
    "I was working in the US at a big tech company. I recently joined a micro finance company. And I could notice the difference between them. The way the teams are structed, the productivity of the Engineers, the way important decisions are made. Everything is so different. Each of them have found themselves a way that works for them.",
    "Meditation helps me calm my mind and think clearly. There was a period last year where I felt blurred and brain fogged all the time. Meditation was the most helpful for me during those times. I suspect it was due to anxiety. I tried a couple of things to find a solution for that problem, like joining a pottery class, going to meetups, hikes, etc. But yoga and meditation was the most helpful of all those. I'm so grateful that I got an opportunity to learn it from a very renouned Guru. I'm very grateful to him for coming into my life. My life transformed completely since then. I've never felt the brain fog since then. It also fixed my eating disorder.",
    "In July this year, I moved back to my parents house. I was concerned about it initially. But now I feel its the best thing that happened to me this year. I feel the safest when I'm home, no stress, no anxiety of any sort. I'm peaceful. I eat healthy, home-cooked food. I come back home to a loving family and people. There is so much care and love. They are the best. I love them. ",
    "I have read 5 books this year, the highest number I've read in any year. It was a weird year for me tbh. I rang New Years in India with my oncall. I was the oncall engineer for New Year. The worst times to be oncall. I somehow managed it. There was some unrelated Redis issue that occured during my shift. I tried my best to mitigate it. I reached out to the respective teams and did everything I could. But my manager took credit for it. I then flew to SF after my vacation and wfh in India. By the end of Feb, things started getting very weird at work. I just couldn't survive it. I decided to move back to India. And I took a 2 weeks off and came to India. After my vacation I went back to US to give it another chance. But soon I realized my manager has kept it against me. So things got weird. And this time I put my resignation",
    "My lived in San Francisco for about a year. I moved there with zero friends. I was fully occupied and focused at work. So I didn't make efforts to meet new people and make new friends. Time flew by and I started feeling lonely and anxious. AI buzz was also booming. I'm just so proud of myself for pushing it through.",
]

# Generated with Claude for this test, so these are AI text by construction.
GENERATED_AI = [
    _sample("samples_staff/clearly_ai.json"),
    "Regular physical activity offers a wide range of benefits for both physical and mental "
    "health. Engaging in exercise helps strengthen the cardiovascular system, improve muscle "
    "tone, and maintain a healthy weight. In addition, physical activity has been shown to "
    "reduce symptoms of anxiety and depression. Experts generally recommend at least 150 "
    "minutes of moderate exercise per week. By incorporating movement into daily routines, "
    "individuals can significantly enhance their overall well-being and quality of life.",
    "Remote work has fundamentally transformed the modern workplace. Organizations that embrace "
    "flexible arrangements often benefit from increased employee satisfaction and access to a "
    "broader talent pool. However, remote work also presents unique challenges, including "
    "communication barriers and feelings of isolation. To address these issues, companies can "
    "invest in collaboration tools, establish clear expectations, and foster a strong virtual "
    "culture. Ultimately, a thoughtful approach to remote work can create value for both "
    "employees and employers.",
    "Climate change is one of the most pressing challenges facing humanity today. Rising global "
    "temperatures are contributing to more frequent extreme weather events, rising sea levels, "
    "and disruptions to ecosystems. Addressing this issue requires a coordinated effort from "
    "governments, businesses, and individuals. Key strategies include transitioning to renewable "
    "energy sources, improving energy efficiency, and protecting natural habitats. By working "
    "together, we can mitigate the impacts of climate change and build a more sustainable future.",
    "Reading is a valuable habit that offers numerous cognitive and emotional benefits. "
    "Regular reading can improve vocabulary, enhance concentration, and strengthen critical "
    "thinking skills. Furthermore, immersing oneself in a good book can reduce stress and "
    "provide a welcome escape from daily pressures. To build a consistent reading habit, it is "
    "helpful to set aside dedicated time each day and choose books that align with personal "
    "interests. Over time, these small efforts can lead to meaningful personal growth.",
]

SCENARIOS = [
    {
        "name": "c1 my own writing",
        "criterion": 1,
        "texts": MY_WRITING,
    },
    {
        "name": "c2 spread: AI set",
        "criterion": 2,
        "texts": GENERATED_AI,
    },
    {
        "name": "c2 spread: human set",
        "criterion": 2,
        # The staff's clearly-human sample plus four of mine.
        "texts": [_sample("samples_staff/clearly_human.json")] + MY_WRITING[2:6],
    },
    {
        "name": "c3 label coverage",
        "criterion": 3,
        # 2 clearly AI, 2 clearly human, 2 borderline. Chosen for what they are,
        # not for what they scored.
        "texts": [
            _sample("samples_staff/clearly_ai.json"),
            GENERATED_AI[1],
            _sample("samples_staff/clearly_human.json"),
            _sample("samples/plain_human.json"),
            _sample("samples_staff/borderline.json"),
            _sample("samples_staff/lightly_edited_ai.json"),
        ],
    },
    # Criterion 4, the appeal path, needs a content_id from a real submission
    # and then an appeal against it, which run_eval.py can't do. It runs
    # separately: `python run_appeal_eval.py --label before`.
    {
        "name": "c5 bad input",
        "criterion": 5,
        # Raw bodies, sent exactly as written. /ping afterwards is checked by
        # run_appeal_eval.py, which runs after this.
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"creator_id": "eval_bad_missing"},
            {"text": None, "creator_id": "eval_bad_null"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems

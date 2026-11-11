
import json
import random
from pathlib import Path

import streamlit as st

# -----------------------------
# ページ設定
# -----------------------------
st.set_page_config(
    page_title="学習アプリ",
    layout="centered",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).parent / "data" / "questions.json"

# -----------------------------
# デザイン（CSS）
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f4f8ff 0%, #ffffff 42%);
    }
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    .hero {
        background: linear-gradient(120deg, #173b68, #2867a5);
        color: white;
        padding: 2rem;
        border-radius: 22px;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 28px rgba(24, 61, 105, .16);
    }
    .hero p { color: #e4efff; margin-bottom: 0; }
    .eyebrow {
        color: #b9d8ff;
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .12em;
    }
    .question-card {
        background: white;
        border: 1px solid #e2eaf5;
        border-radius: 18px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 5px 18px rgba(32, 65, 105, .06);
        margin: .8rem 0 1rem 0;
    }
    .muted { color: #64748b; font-size: .9rem; }
    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 12px;
        min-height: 2.8rem;
        font-weight: 700;
    }
    [data-testid="stMetric"] {
        background: white;
        border: 1px solid #e2eaf5;
        padding: 12px 16px;
        border-radius: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# 問題データの読み込み
# -----------------------------
@st.cache_data
def load_questions():
  with DATA_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

  # データの最低限の形式チェック
  required = {
      "id", "grade", "subject", "unit", "difficulty",
      "question", "choices", "answer", "explanation"
  }

  for number, question in enumerate(data, start=1):
    missing = required - question.keys()

    if missing:
      raise ValueError(
          f"{number}番目の問題に必要な項目がありません: {missing}"
      )

    # answerは選択肢の番号（0から始まる整数）
    answer = question["answer"]

    if (
        not isinstance(answer, int)
        or not (0 <= answer < len(question["choices"]))
    ):
      raise ValueError(
          f"問題 {question['id']} の正解番号が不正です"
      )

  return data


try:
  all_questions = load_questions()

except Exception as error:
  st.error(
      "問題データを読み込めませんでした。"
      "data/questions.json を確認してください。"
  )
  st.exception(error)
  st.stop()


# -----------------------------
# セッション状態
# -----------------------------
defaults = {
    "page": "home",
    "quiz": [],
    "index": 0,
    "answers": {},
    "last_result": None,
}

for key, value in defaults.items():
  if key not in st.session_state:
    st.session_state[key] = value


def start_quiz(selected_grade, selected_subject, selected_level, count):
  pool = [
      q for q in all_questions
      if q["grade"] == selected_grade
      and q["subject"] == selected_subject
      and (
          selected_level == "すべて"
          or q["difficulty"] == selected_level
      )
  ]

  random.shuffle(pool)

  st.session_state.quiz = pool[:count]
  st.session_state.index = 0
  st.session_state.answers = {}
  st.session_state.last_result = None
  st.session_state.page = "quiz"


def reset_to_home():
  st.session_state.page = "home"
  st.session_state.quiz = []
  st.session_state.index = 0
  st.session_state.answers = {}
  st.session_state.last_result = None


# -----------------------------
# サイドバー
# -----------------------------
with st.sidebar:
  st.markdown("## 📚 まいにちドリル")
  st.caption("毎日の学習を、少しずつ。")

  st.divider()

  st.markdown("### このアプリについて")
  st.write("小学生・中学生向けの四択学習アプリです。")
  st.write("学年・教科・難易度を選び、問題に挑戦できます。")

  st.divider()

  st.caption(f"登録問題数：{len(all_questions)}問")
  st.caption("※現在は学習用サンプル問題を収録しています。")


# -----------------------------
# ヘッダー
# -----------------------------
st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">LEARN A LITTLE EVERY DAY</div>
      <h1 style="margin:.35rem 0 .5rem 0;">まいにちドリル 📚</h1>
      <p>今日の一問が、明日の自信になる。</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# ホーム画面
# -----------------------------
if st.session_state.page == "home":

  st.subheader("今日の学習メニュー")
  st.write("自分に合った学年・教科を選んで、学習を始めましょう。")

  grades = sorted(
      {q["grade"] for q in all_questions},
      key=lambda x: (
          0 if x.startswith("小学") else 1,
          int(x[2])
      )
  )

  selected_grade = st.selectbox("① 学年を選択", grades)

  available_subjects = sorted({
      q["subject"]
      for q in all_questions
      if q["grade"] == selected_grade
  })

  selected_subject = st.selectbox(
      "② 教科を選択",
      available_subjects
  )

  available_levels = sorted({
      q["difficulty"]
      for q in all_questions
      if q["grade"] == selected_grade
      and q["subject"] == selected_subject
  })

  level_options = ["すべて"] + available_levels

  selected_level = st.selectbox(
      "③ 難易度を選択",
      level_options
  )

  matching_count = sum(
      1 for q in all_questions
      if q["grade"] == selected_grade
      and q["subject"] == selected_subject
      and (
          selected_level == "すべて"
          or q["difficulty"] == selected_level
      )
  )

  left, right = st.columns(2)

  left.metric("出題できる問題", f"{matching_count} 問")
  right.metric("対象学年", selected_grade)

  if matching_count == 0:
    st.warning("この条件に合う問題はまだ登録されていません。")

  else:
    question_count = st.slider(
        "④ 出題する問題数",
        min_value=1,
        max_value=matching_count,
        value=min(5, matching_count),
    )

    st.info(
        "問題は登録データからランダムに選ばれます。"
        "回答後には解説を確認できます。"
    )

    if st.button(
        "🚀 学習をスタート",
        type="primary",
        use_container_width=True
    ):
      start_quiz(
          selected_grade,
          selected_subject,
          selected_level,
          question_count
      )
      st.rerun()

  st.divider()

  st.subheader("学習のポイント")

  c1, c2, c3 = st.columns(3)

  c1.markdown("**🎯 目標を決める**\n\n学年と教科を選択")
  c2.markdown("**✏️ 自分で考える**\n\n四択問題に挑戦")
  c3.markdown("**💡 解説で復習**\n\n答えの理由を確認")


# -----------------------------
# クイズ画面
# -----------------------------
elif st.session_state.page == "quiz":

  quiz = st.session_state.quiz
  total = len(quiz)
  index = st.session_state.index

  if not quiz:
    st.warning("問題がありません。ホームに戻ってください。")

    if st.button("ホームに戻る"):
      reset_to_home()
      st.rerun()

    st.stop()

  if index >= total:
    st.session_state.page = "result"
    st.rerun()

  question = quiz[index]
  question_id = question["id"]

  answered = question_id in st.session_state.answers

  st.markdown(
      f"**{question['grade']}　/　"
      f"{question['subject']}　/　{question['unit']}**"
  )

  st.progress((index + (1 if answered else 0)) / total)

  a, b = st.columns(2)

  a.metric("問題", f"{index + 1} / {total}")
  b.metric("回答済み", f"{len(st.session_state.answers)} 問")

  st.markdown(
      f"""
        <div class="question-card">
          <div class="muted">
            QUESTION {index + 1:02d}　・　{question['difficulty']}
          </div>
          <h3 style="margin:.6rem 0 0 0;">
            {question['question']}
          </h3>
        </div>
        """,
      unsafe_allow_html=True,
  )

  if not answered:

    with st.form(key=f"answer-form-{question_id}"):

      selected_answer = st.radio(
          "正しいと思う答えを選んでください",
          question["choices"],
          index=None,
      )

      submitted = st.form_submit_button(
          "この答えで決定する",
          type="primary",
          use_container_width=True,
      )

      if submitted:

        if selected_answer is None:
          st.warning("選択肢を選んでください。")

        else:
          st.session_state.answers[question_id] = selected_answer
          st.rerun()

  else:

    selected_answer = st.session_state.answers[question_id]

    # 正解番号から正解の選択肢を取得
    correct_answer = question["choices"][question["answer"]]

    is_correct = selected_answer == correct_answer

    if is_correct:
      st.success("正解！よくできました！ 🎉")
    else:
      st.error("今回は不正解です。次の復習に活かしましょう。")

    st.markdown(f"**あなたの回答：** {selected_answer}")
    st.markdown(f"**正解：** {correct_answer}")

    st.info(f"💡 **解説**\n\n{question['explanation']}")

    if index + 1 < total:
      button_label = "次の問題へ →"
    else:
      button_label = "結果を見る →"

    if st.button(
        button_label,
        type="primary",
        use_container_width=True
    ):
      st.session_state.index += 1
      st.rerun()

  st.divider()

  if st.button("学習を中断してホームへ戻る"):
    reset_to_home()
    st.rerun()


# -----------------------------
# 結果画面
# -----------------------------
elif st.session_state.page == "result":

  quiz = st.session_state.quiz
  total = len(quiz)

  # 正解数を計算
  correct = sum(
      1 for q in quiz
      if st.session_state.answers.get(q["id"])
      == q["choices"][q["answer"]]
  )

  rate = correct / total if total else 0

  st.balloons()

  st.subheader("学習結果")
  st.markdown("### お疲れさまでした！")

  x, y = st.columns(2)

  x.metric("正解数", f"{correct} / {total}")
  y.metric("正答率", f"{rate:.0%}")

  st.progress(rate)

  if rate == 1:
    st.success("満点です！すばらしい！")

  elif rate >= 0.6:
    st.success("よく頑張りました。間違えた問題を復習しましょう。")

  else:
    st.info("解説を読み返して、もう一度挑戦してみましょう。")

  st.markdown("### 問題ごとの振り返り")

  for number, q in enumerate(quiz, start=1):

    user_answer = st.session_state.answers.get(
        q["id"],
        "未回答"
    )

    correct_answer = q["choices"][q["answer"]]

    ok = user_answer == correct_answer

    with st.expander(
        f"{'⭕' if ok else '❌'} 問題{number}：{q['question']}"
    ):

      st.write(f"あなたの回答：{user_answer}")
      st.write(f"正解：{correct_answer}")
      st.write(f"解説：{q['explanation']}")

  if st.button(
      "別の問題に挑戦する",
      type="primary",
      use_container_width=True
  ):
    reset_to_home()
    st.rerun()


# -----------------------------
# フッター
# -----------------------------
st.divider()
st.caption("まいにちドリル ｜ 学習用サンプルアプリ")

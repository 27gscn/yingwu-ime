// Exercises the shipping RimeEngine directly: code annotation, reading
// selection for polyphonic characters, and the Western-mode toggle.
//
// Must run from <root>\x64\ so RimeEngine finds rime.dll beside it and the
// data directory at ..\data, exactly as the text service does.
#include <windows.h>

#include <cstdio>
#include <string>

#include "RimeEngine.h"

namespace {

void Print(const std::wstring& text) {
  if (text.empty()) return;
  const int size = WideCharToMultiByte(CP_UTF8, 0, text.c_str(), -1, nullptr,
                                       0, nullptr, nullptr);
  if (size <= 0) return;
  std::string buffer(static_cast<size_t>(size), '\0');
  WideCharToMultiByte(CP_UTF8, 0, text.c_str(), -1, buffer.data(), size,
                      nullptr, nullptr);
  fputs(buffer.c_str(), stdout);
}

int failures = 0;

void Case(hengma::RimeEngine* engine, const char* keys, int show) {
  engine->Clear();
  hengma::EngineSnapshot snapshot;
  for (const char* p = keys; *p; ++p) {
    snapshot = engine->ProcessKey(static_cast<int>(*p), 0);
  }
  printf("  %-24s -> ", keys);
  const int total = static_cast<int>(snapshot.candidates.size());
  const int n = total < show ? total : show;
  for (int i = 0; i < n; ++i) {
    const hengma::Candidate& candidate = snapshot.candidates[i];
    printf(" ");
    Print(candidate.text);
    if (!candidate.comment.empty()) {
      printf("[");
      Print(candidate.comment);
      printf("]");
    }
  }
  if (total == 0) printf(" (no candidates)");
  printf("\n");
}

void Expect(const char* label, bool ok) {
  printf("  %-40s %s\n", label, ok ? "PASS" : "FAIL");
  if (!ok) ++failures;
}

std::wstring CommentOf(hengma::RimeEngine* engine, const char* keys,
                       const wchar_t* want_text) {
  engine->Clear();
  hengma::EngineSnapshot snapshot;
  for (const char* p = keys; *p; ++p) {
    snapshot = engine->ProcessKey(static_cast<int>(*p), 0);
  }
  for (const hengma::Candidate& candidate : snapshot.candidates) {
    if (candidate.text == want_text) return candidate.comment;
  }
  return L"(not found)";
}

}  // namespace

int main() {
  SetConsoleOutputCP(CP_UTF8);
  hengma::RimeEngine engine;
  printf("initializing (first run compiles dictionaries)...\n");
  fflush(stdout);
  if (!engine.Initialize(nullptr)) {
    printf("FAILED: engine did not initialize\n");
    return 1;
  }
  printf("ready\n\n");

  printf("candidates with their complete code:\n");
  Case(&engine, "qing", 5);
  Case(&engine, "qingz", 5);
  Case(&engine, "qingzs", 5);
  Case(&engine, "ying", 5);
  Case(&engine, "hang", 3);
  Case(&engine, "xing", 3);
  Case(&engine, "tiandi", 5);
  Case(&engine, "tiandidd", 3);
  Case(&engine, "tiandiddzt", 3);
  Case(&engine, "qiufengzh", 3);

  printf("\nchecks:\n");
  Expect("清 under `qingzs` is annotated qingzs",
         CommentOf(&engine, "qingzs", L"清") == L"qingzs");
  Expect("应 under `ying` is annotated yingbg",
         CommentOf(&engine, "ying", L"应") == L"yingbg");
  // 行 has three readings; only the one being typed should show.
  Expect("行 under `hang` shows only hangzx",
         CommentOf(&engine, "hang", L"行") == L"hangzx");
  Expect("行 under `xing` shows only xingzx",
         CommentOf(&engine, "xing", L"行") == L"xingzx");
  Expect("phrases carry no character code",
         CommentOf(&engine, "tiandiddzt", L"天地").empty());

  // 天地 is the worked example in the README: two levels of suffix, each one
  // narrowing the set. CommentOf yields "(not found)" when the phrase is
  // absent and an empty comment when it is present.
  Expect("天地 is reachable by the base code alone",
         CommentOf(&engine, "tiandi", L"天地") != L"(not found)");
  Expect("田地 survives the base code",
         CommentOf(&engine, "tiandi", L"田地") != L"(not found)");
  Expect("first suffix drops 田地",
         CommentOf(&engine, "tiandidd", L"田地") == L"(not found)");
  Expect("first suffix keeps 天敌",
         CommentOf(&engine, "tiandidd", L"天敌") != L"(not found)");
  Expect("second suffix leaves only 天地",
         CommentOf(&engine, "tiandiddzt", L"天敌") == L"(not found)");
  Expect("qiufengzh separates 秋风 from 球风",
         CommentOf(&engine, "qiufengzh", L"秋风") != L"(not found)" &&
             CommentOf(&engine, "qiufengzh", L"球风") == L"(not found)");

  // Chinese text wants Chinese marks. The engine is handed the plain ASCII
  // character; librime's punctuator is what turns it into the full-width form.
  printf("\nChinese punctuation:\n");
  struct Mark {
    char key;
    const wchar_t* want;
    const char* name;
  };
  const Mark marks[] = {
      {',', L"，", "comma"},     {'.', L"。", "full stop"},
      {'?', L"？", "question"},  {'!', L"！", "exclamation"},
      {';', L"；", "semicolon"}, {':', L"：", "colon"},
      {'\\', L"、", "enumeration comma"},
  };
  for (const Mark& mark : marks) {
    engine.Clear();
    const hengma::EngineSnapshot snapshot =
        engine.ProcessKey(static_cast<int>(mark.key), 0);
    char label[72] = {};
    sprintf_s(label, "%s becomes its Chinese form", mark.name);
    Expect(label, snapshot.commit == mark.want);
  }

  printf("\nWestern-mode toggle:\n");
  engine.Clear();
  Expect("starts in Chinese mode", !engine.IsAsciiMode());
  Expect("toggle turns Western mode on", engine.ToggleAsciiMode());
  Expect("IsAsciiMode agrees", engine.IsAsciiMode());
  Expect("toggle turns it back off", !engine.ToggleAsciiMode());
  Expect("back in Chinese mode", !engine.IsAsciiMode());
  engine.Clear();
  Expect("Chinese mode still produces candidates",
         !CommentOf(&engine, "qingzs", L"清").empty());

  printf("\n%s (%d failure%s)\n", failures ? "FAILED" : "ALL CHECKS PASSED",
         failures, failures == 1 ? "" : "s");
  return failures ? 1 : 0;
}

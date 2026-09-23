// Read-only probe: asks TSF itself which keyboard text services are
// registered for Simplified Chinese, and whether ours is among them.
#include <windows.h>
#include <msctf.h>
#include <objbase.h>
#include <cstdio>

static const CLSID kHengma = {
    0x57a9a4da, 0x60e5, 0x426d,
    {0xa2, 0x20, 0x5c, 0x16, 0x2c, 0x97, 0x6c, 0xaa}};

int main() {
  SetConsoleOutputCP(CP_UTF8);
  CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);

  ITfInputProcessorProfiles* profiles = nullptr;
  HRESULT hr = CoCreateInstance(CLSID_TF_InputProcessorProfiles, nullptr,
                                CLSCTX_INPROC_SERVER,
                                IID_ITfInputProcessorProfiles,
                                reinterpret_cast<void**>(&profiles));
  if (FAILED(hr)) {
    printf("CoCreateInstance failed: 0x%08lX\n", hr);
    return 1;
  }

  IEnumTfLanguageProfiles* enumerator = nullptr;
  hr = profiles->EnumLanguageProfiles(MAKELANGID(LANG_CHINESE,
                                                 SUBLANG_CHINESE_SIMPLIFIED),
                                      &enumerator);
  if (FAILED(hr) || !enumerator) {
    printf("EnumLanguageProfiles failed: 0x%08lX\n", hr);
    profiles->Release();
    return 1;
  }

  printf("registered zh-CN keyboard text services:\n");
  TF_LANGUAGEPROFILE profile = {};
  ULONG fetched = 0;
  bool found = false;
  while (enumerator->Next(1, &profile, &fetched) == S_OK && fetched == 1) {
    if (!IsEqualGUID(profile.catid, GUID_TFCAT_TIP_KEYBOARD)) continue;

    BSTR description = nullptr;
    profiles->GetLanguageProfileDescription(profile.clsid, profile.langid,
                                            profile.guidProfile, &description);
    BOOL enabled = FALSE;
    profiles->IsEnabledLanguageProfile(profile.clsid, profile.langid,
                                       profile.guidProfile, &enabled);

    wchar_t clsid_text[40] = {};
    StringFromGUID2(profile.clsid, clsid_text, 40);
    const bool mine = IsEqualCLSID(profile.clsid, kHengma);
    if (mine) found = true;

    wprintf(L"  %s  enabled=%d  %s%s\n", clsid_text, enabled ? 1 : 0,
            description ? description : L"(no description)",
            mine ? L"   <== Hengma Native 0.3.0-alpha" : L"");
    if (description) SysFreeString(description);
  }

  printf("\nHengma Native profile visible to TSF: %s\n", found ? "YES" : "NO");
  enumerator->Release();
  profiles->Release();
  CoUninitialize();
  return found ? 0 : 2;
}

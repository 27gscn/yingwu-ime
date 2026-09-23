#include "Globals.h"

HINSTANCE g_hInst = nullptr;
LONG g_cRefDll = -1;  // Microsoft TSF sample convention: -1 means no refs.
CRITICAL_SECTION g_cs;

// {57A9A4DA-60E5-426D-A220-5C162C976CAA}
const CLSID c_clsidTextService = {
    0x57a9a4da,
    0x60e5,
    0x426d,
    {0xa2, 0x20, 0x5c, 0x16, 0x2c, 0x97, 0x6c, 0xaa}};

// {C22C0423-C953-4D85-8C80-B472511A79E7}
const GUID c_guidProfile = {
    0xc22c0423,
    0xc953,
    0x4d85,
    {0x8c, 0x80, 0xb4, 0x72, 0x51, 0x1a, 0x79, 0xe7}};

// {35C3B3A4-DC91-41AF-829A-367F9E4B420E}
// Preserved key for the Shift tap that switches Chinese/Western input.
const GUID c_guidToggleAsciiKey = {
    0x35c3b3a4,
    0xdc91,
    0x41af,
    {0x82, 0x9a, 0x36, 0x7f, 0x9e, 0x4b, 0x42, 0x0e}};

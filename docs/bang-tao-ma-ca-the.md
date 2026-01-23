# Bảng tạo mã cá thể

- Mã user: ETS-YYMMDD-XXXX

## Quy ước mã cho từng thực thể

### 1. Profile
- Cấu trúc: PRF-<ENTITYCODE>-<V>
- Giải nghĩa: `PRF` là loại thực thể; `ENTITYCODE` là mã cá thể (sử dụng entity_short, tức là phần YYMMDD-XXXX của ETS); `V` (XX) là version.
- Ví dụ: PRF-260122-A1B2-01

### 2. Education
- Cấu trúc: EDU-<entity_short>-<SEQ>
- Giải nghĩa: `EDU` là loại thực thể education; `entity_short` lấy từ mã cá thể; `SEQ` (XXXX) là số thứ tự.
- Ví dụ: EDU-260122-A1B2-0001

### 3. Identity Documents
- Cấu trúc: IDN-<entity_short>-<SEQ>
- Giải nghĩa: `IDN` là loại giấy tờ tùy thân; `entity_short` là phần rút gọn của mã cá thể; `SEQ` (XXXX) là giấy tờ thứ mấy trong profile.
- Ví dụ: IDN-260122-A1B2-0001

### 4. Wallets
- Cấu trúc: WETS-<entity_short>
- Giải nghĩa: `WETS` là loại thực thể Wallet ETS; `entity_short` là phần rút gọn của mã cá thể.
- Ví dụ: WETS-260122-A1B2

### 5. Wallet Assets
- Cấu trúc: WAS-<entity_short>-<ASSET_CODE>
- Giải nghĩa: `WAS` là loại thực thể Wallet Asset; `entity_short` là phần rút gọn của mã cá thể; `ASSET_CODE` là mã tài sản (ví dụ: BADGE_TOP10, CERT_IELTS…).
- Ví dụ: WAS-260122-A1B2-BADGE_TOP10

### 6. Asset Rates To Credit
- Cấu trúc: RTE-<From_Asset_Type>-<V>
- Giải nghĩa: `RTE` là loại thực thể Rate; `From_Asset_Type` là loại tài sản nguồn; `V` (XX) là version chính sách quy đổi.
- Ví dụ: RTE-BADGE-01

### 7. Wallet Transactions
- Cấu trúc: TX-<entity_short>-<T>-<SEQ>
- Giải nghĩa: `TX` là giao dịch ví; `entity_short` là phần rút gọn của mã cá thể; `T` là loại giao dịch (E = Earn, S = Spend, C = Convert); `SEQ` (XXXX) là số thứ tự tăng dần theo từng wallet.
- Ví dụ: TX-260122-A1B2-E-0001

### 8. User Interests
- Cấu trúc: INT-<entity_short>-<SEQ>
- Giải nghĩa: `INT` là thực thể Interest; `entity_short` là phần rút gọn của mã cá thể; `SEQ` (XXXX) là số thứ tự sở thích của cá thể.
- Ví dụ: INT-260122-A1B2-0001

### 9. Interest Canonical
- Cấu trúc: ICN-<SEQ>
- Giải nghĩa: `ICN` là thực thể Interest CaNoNical; `SEQ` (XXXX) là số thứ tự tăng dần.
- Ví dụ: ICN-0001

### 10. Posts
- Cấu trúc: PST-<entity_short>-<SEQ>
- Giải nghĩa: `PST` là thực thể Post; `entity_short` là phần rút gọn của mã cá thể; `SEQ` (XXXX) là số thứ tự tăng dần theo cá thể.
- Ví dụ: PST-260122-A1B2-0001

### 11. Comments
- Cấu trúc: CMT-<entity_short>-<SEQ>
- Giải nghĩa: `CMT` là thực thể Comment; `entity_short` là phần rút gọn của mã cá thể; `SEQ` (XXXX) là số thứ tự tăng dần theo cá thể.
- Ví dụ: CMT-260122-A1B2-0001

### 12. Post Interactions
- Cấu trúc: PINT-<entity_short>-<ACTION>-<SEQ>
- Giải nghĩa: `PINT` là thực thể Post Interaction; `entity_short` là phần rút gọn của mã cá thể; `ACTION` là loại tương tác (L = Like, S = Share); `SEQ` (XXXX) là số thứ tự tăng dần theo từng profile.
- Ví dụ: PINT-260122-A1B2-L-0001

### 13. Comment Interactions
- Cấu trúc: CINT-<entity_short>-<ACTION>-<SEQ>
- Giải nghĩa: `CINT` là thực thể Comment Interaction; `entity_short` là phần rút gọn của mã cá thể; `ACTION` giống post_interactions; `SEQ` (XXXX) là số thứ tự tăng dần.
- Ví dụ: CINT-260122-A1B2-L-0001

### 14. Messages
- Cấu trúc: MSG-<entity_short>-<SCOPE>-<SEQ>
- Giải nghĩa: `MSG` là thực thể Message; `entity_short` là phần rút gọn của mã cá thể; `SCOPE` (1 digit) là loại tin nhắn (0 = cá nhân, 1 = nhóm); `SEQ` (XXXX) là số thứ tự tăng dần theo sender.
- Ví dụ: MSG-260122-A1B2-0-0001

### 15. User Actions
- Cấu trúc: ACT-<entity_short>-<TYPE>-<SEQ>
- Giải nghĩa: `ACT` là thực thể User Action; `entity_short` là phần rút gọn của mã cá thể; `TYPE` là loại hành động (MSG, JOIN, LEAVE, LIKE, SHARE, CMT, POST…); `SEQ` (XXXX) là số thứ tự tăng dần theo cá thể.
- Ví dụ: ACT-260122-A1B2-JOIN-0001

### 16. Polls
- Cấu trúc: POL-<SEQ>
- Giải nghĩa: `POL` là thực thể Poll; `SEQ` (XXXX) là số thứ tự tăng dần.
- Ví dụ: POL-0001

### 17. Poll Options
- Cấu trúc: OPT-<SEQ>
- Giải nghĩa: `OPT` là thực thể Poll Option; `SEQ` (XXXX) là số thứ tự tăng dần.
- Ví dụ: OPT-0001

### 18. Poll Votes
- Cấu trúc: PVT-<entity_short>-<SEQ>
- Giải nghĩa: `PVT` là thực thể Poll Vote; `entity_short` là phần rút gọn của mã cá thể; `SEQ` (XXXX) là số thứ tự tăng dần theo cá thể.
- Ví dụ: PVT-260122-A1B2-0001

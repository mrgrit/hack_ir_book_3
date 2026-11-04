# 저자용 재현 절차

실습 독자는 DOCX와 examples/chapter01·examples/chapter02의 명령을 한 개씩 사용한다. 아래는 조판·검증 담당자의 명령이다. 실행 위치는 이 저장소의 루트이며 경로를 자신의 별도 사본에 맞춘다. 출력 파일·폴더가 이미 있으면 새 경로를 정한다.

## 실행 환경

조판은 Windows 11 PowerShell, Codex 번들 Python, Microsoft Word COM 읽기 전용 export, 번들 Poppler에서 수행했다. Python·패키지 버전과 도구 해시는 verification 기록을 따른다. 1장의 Ubuntu 터미널 명령은 Git Bash 문법 검사와 코드 대조를 했다. 2장은 기존 Ubuntu 22.04의 Python 3.10.12에서 파일 검사·적재를 실행했다. Ubuntu 설치부터 재현한 시험은 아니다.

생성·검사는 Python 표준 라이브러리만 필요하다. 표본 분석에는 openpyxl, 원고 조판에는 python-docx·Pillow, 검수에는 pdf2image·pypdf가 추가로 필요하다. 저자 도구의 의존성을 독자에게 일괄 설치하도록 요구하지 않는다.

```bash
BOOK3_SOURCE=../hack_ir_with_wazuh_source/purple-agg python3 -m unittest discover -s tests -v
python3 tools/audit_generator.py --source ../hack_ir_with_wazuh_source/purple-agg --out build/generator-probes.json
```

BOOK3_SOURCE가 없으면 통합 생성 시험 1개가 skip된다. 성공 보고 전에 skip 수를 확인한다. PowerShell에서는 `$env:BOOK3_SOURCE`에 절대 경로를 지정한 뒤 unittest를 실행한다. 소스는 README에 지정한 커밋과 변경 없는 추적 파일이어야 한다. 강의 저장소에 교재 코드를 복사하지 않는다.

## 집계 표본 재계산

Drive에서 권한 있는 사용자가 파일 3개를 저장소 밖 `../private-inputs`에 준비한다. 파일명은 원본 날짜를 유지한다. 아래 도구는 기본적으로 중복 열을 거부한다. 이번 기록은 원본 도구와 비교하기 위해 마지막 중복 열 선택을 명시했다. 그 선택이 원 집계 정의의 확정을 뜻하지는 않는다.

```bash
python3 tools/profile_labeling.py ../private-inputs/labeling_2019-05-26.xlsx ../private-inputs/labeling_2019-05-27.xlsx ../private-inputs/labeling_2019-05-30.xlsx --duplicate-column last --out build/sample-statistics.json
```

날짜별 스냅샷 통계와 출발지별 최신 행의 합집합을 따로 출력한다. 행 수를 원시 이벤트 수로 바꾸어 설명하지 않는다. 보고서에는 식별자를 내보내지 않는다. `Counter.ipynb`는 계산 정의를 제공하지 않아 실행하지 않았고 pickle도 역직렬화하지 않았다.

## DOCX 재생성

```bash
python3 tools/figures.py
python3 tools/write_chapter01.py
python3 tools/build_docx.py --output manuscript/volume03-chapter01.docx
```

write_chapter01.py는 저자용 구조화 원고와 복사용 명령을 함께 갱신한다. 본문 수정은 이 파일에서 시작한다. build_docx.py는 tools/assets/bookk-B5.docx를 base로 연다. 원고의 JSON만 직접 고치면 다음 write_chapter01 실행에서 덮어쓰이므로 수정 위치를 통일한다.

인물 삽화는 생성된 PNG를 보존한다. imagegen 프롬프트와 인체·시점 검수 기록은 illustration-record.json에 있다. figures.py는 구성·시간·준비 흐름의 도식만 만든다.

Windows 렌더 명령은 다음과 같다. Microsoft Word가 설치되어 있어야 하며 사용자 문서는 읽기 전용으로 열고 저장하지 않는다. OutputFile은 검사 전용 build 아래에 둔다.

```powershell
.\tools\render_docx_windows.ps1 -InputFile manuscript\volume03-chapter01.docx -OutputFile build\review\chapter01.pdf
python tools\rasterize.py build\review\chapter01.pdf --out build\review --poppler 'POPPLER_BIN_PATH'
```

`POPPLER_BIN_PATH`는 사용할 Poppler bin의 실제 경로로 바꾼다. 이번 실행은 Codex 번들 런타임을 사용했다. PDF를 배포하지 않는다. 모든 쪽에서 제목·본문·표·명령·전체 URL·그림을 확인하고, 원고에 내장한 그림 해시를 현재 자산과 대조한다.

## 2장 재현

본문과 복사용 요청은 다음 순서로 갱신한다. 그림 자르기는 보존된 실제 화면 파일을 사용한다. 인물 원본 PNG를 새로 생성하지 않는다.

```bash
python3 tools/queries_chapter02.py
python3 tools/write_chapter02.py
python3 tools/figures_chapter02.py
python3 tools/build_docx.py --source manuscript/volume03-chapter02.json --output manuscript/volume03-chapter02.docx
python3 tools/verify_chapter02.py build/r01-pilot01 editorial/chapter02-query-results.json --out build/chapter02-data-verification.json
```

마지막 명령은 네트워크 요청 없이 1장의 원본 생성 파일과 저장된 14개 실제 응답을 대조한다. 같은 manifest와 bulk 해시가 필요하다. 다른 기준일·규모의 파일을 과거 응답과 대조하지 않는다.

실제 적재는 2장 본문과 `examples/chapter02/commands.sh`를 따라 kt66 호스트에서 수행한다. `load_dataset.py`는 해시 검사를 선행하며 정확한 전용 인덱스가 없는 경우에만 만든다. 기존 인덱스에서는 중단하므로 보존 중인 검토용 인덱스에 적재를 반복하지 않는다. partial bulk 실패에서는 현재 인덱스를 보존하고 오류를 조사한다.

독자용 도구는 Python 표준 라이브러리를 사용하며 비밀번호는 실행 시 getpass로 입력한다. `--insecure`는 본문의 kt66 자체 서명 인증서 실습에만 사용한다. 인증서를 검증할 환경은 `--ca-cert` 경로를 지정한다. 실제 시험 범위와 남겨 둔 saved object는 `chapter02-review.md`를 따른다.

## 3장 재현

```bash
python3 tools/queries_chapter03.py
python3 tools/write_chapter03.py
python3 tools/figures_chapter03.py
python3 tools/build_docx.py --source manuscript/volume03-chapter03.json --output manuscript/volume03-chapter03.docx
python3 tools/verify_chapter03.py build/r02-ch03 editorial/chapter03-query-results.json --out build/chapter03-data-verification.json
```

원문 생성 명령은 3장과 `examples/chapter03/commands.sh`를 따른다. 저장된 응답과 대조할 때는 동일한 manifest·bulk 해시의 자료를 사용한다. Windows Word 렌더와 모든 쪽의 개별 검수 후 `verify_artifact.py 3 build/검수폴더/chapter03.pdf --reviewed-all-pages`를 실행하면 내장 그림·URL·쿼리·판형을 기록한다. 이 옵션은 실제로 모든 지면을 확인한 뒤에만 지정한다.

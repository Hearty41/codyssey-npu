import json
import time

# 1. 라벨(이름표) 통일하기: '+', 'cross' -> 'Cross' / 'x', 'X' -> 'X'
def normalize_label(raw_label):
    label = str(raw_label).strip().lower()
    if label in ["+", "cross"]:
        return "Cross"
    elif label == "x":
        return "X"
    return raw_label

# 2. MAC 연산 함수: 같은 위치의 숫자끼리 곱하고 모두 더하기
def mac_operation(pattern, filter_matrix):
    size = len(pattern)
    total_score = 0.0
    
    for r in range(size):          # 위에서 아래로 한 줄씩 (행)
        for c in range(size):      # 왼쪽에서 오른쪽으로 한 칸씩 (열)
            total_score += pattern[r][c] * filter_matrix[r][c]
            
    return total_score

# 3. 점수 비교 및 판정 함수 (허용오차 epsilon = 1e-9 적용)
def judge_scores(score_a, score_b, label_a="A", label_b="B", epsilon=1e-9):
    if abs(score_a - score_b) < epsilon:
        return "UNDECIDED"
    elif score_a > score_b:
        return label_a
    else:
        return label_b

# 4. 성능 측정 함수: 지정된 횟수만큼 MAC 연산을 반복하고 평균 시간(ms) 반환
def measure_mac_time(pattern, filter_matrix, repeat=10):
    start_time = time.perf_counter()
    for _ in range(repeat):
        mac_operation(pattern, filter_matrix)
    end_time = time.perf_counter()
    
    avg_ms = ((end_time - start_time) / repeat) * 1000
    return avg_ms

# 5. 모드 1용 3x3 배열 입력 함수 (검증 및 재입력 유도 포함)
def input_matrix_3x3(name):
    print(f"\n{name} (3줄 입력, 공백 구분)")
    matrix = []
    row_idx = 0
    
    while row_idx < 3:
        line = input(f"  {row_idx + 1}행 입력: ").strip()
        parts = line.split()
        
        if len(parts) != 3:
            print("입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.")
            continue
            
        try:
            row = [float(x) for x in parts]
            matrix.append(row)
            row_idx += 1
        except ValueError:
            print("입력 형식 오류: 숫자만 공백으로 구분해 입력하세요.")
            
    return matrix

# 6. 모드 1 실행 함수 (사용자 입력 3x3)
def run_mode_1():
    print("\n#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = input_matrix_3x3("필터 A")
    filter_b = input_matrix_3x3("필터 B")
    
    print("\n[저장 확인] 필터 A, B 입력 완료!")
    
    print("\n#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = input_matrix_3x3("패턴")
    
    # MAC 연산 및 판정
    score_a = mac_operation(pattern, filter_a)
    score_b = mac_operation(pattern, filter_b)
    result = judge_scores(score_a, score_b, label_a="A", label_b="B")
    
    # 성능 측정 (10회 반복 평균)
    avg_time_ms = measure_mac_time(pattern, filter_a, repeat=10)
    
    print("\n#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"A 점수: {score_a:.4f}" if score_a % 1 != 0 else f"A 점수: {score_a}")
    print(f"B 점수: {score_b:.4f}" if score_b % 1 != 0 else f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.4f} ms")
    
    if result == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {result}")
        
    print("\n#---------------------------------------")
    print("# [4] 성능 분석 (3×3)")
    print("#---------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 38)
    print(f"{'3×3':<10} {avg_time_ms:<15.4f} {3 * 3}")

# 7. 배열 크기(N x N) 검증 도우미 함수
def is_valid_square_matrix(matrix, expected_size):
    if not isinstance(matrix, list) or len(matrix) != expected_size:
        return False
    for row in matrix:
        if not isinstance(row, list) or len(row) != expected_size:
            return False
    return True

# 8. 모드 2 실행 함수 (data.json 분석 및 전체 성능 측정)
def run_mode_2(filepath="data.json"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"\n[오류] '{filepath}' 파일을 찾을 수 없습니다.")
        return
    except json.JSONDecodeError:
        print(f"\n[오류] '{filepath}' 파일의 JSON 형식이 올바르지 않습니다.")
        return

    raw_filters = data.get("filters", {})
    raw_patterns = data.get("patterns", {})

    # [1] 필터 로드 및 라벨 정규화 ('cross' -> 'Cross', 'x' -> 'X')
    filters = {}
    print("\n#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")
    for size_key, filter_dict in raw_filters.items():
        normalized_dict = {}
        for k, mat in filter_dict.items():
            std_key = normalize_label(k)
            normalized_dict[std_key] = mat
        filters[size_key] = normalized_dict
        loaded_labels = ", ".join(normalized_dict.keys())
        print(f"✓ {size_key:<8} 필터 로드 완료 ({loaded_labels})")

    # [2] 패턴 분석
    print("\n#---------------------------------------")
    print("# [2] 패턴 분석 (라벨 정규화 적용)")
    print("#---------------------------------------")
    
    total_count = 0
    pass_count = 0
    fail_list = []
    bench_samples = {}  # 크기별 성능 측정을 위해 샘플 1개씩 저장

    for pat_key, pat_info in raw_patterns.items():
        total_count += 1
        print(f"-- {pat_key} ---")

        # 키에서 크기 N 추출 (예: 'size_5_1' -> 5)
        try:
            parts = pat_key.split("_")
            n_size = int(parts[1])
            size_key = f"size_{n_size}"
        except (IndexError, ValueError):
            reason = f"잘못된 패턴 키 형식 ({pat_key})"
            print(f"판정: FAIL | 사유: {reason}")
            fail_list.append((pat_key, reason))
            continue

        # 해당 크기의 필터 존재 여부 확인
        if size_key not in filters or "Cross" not in filters[size_key] or "X" not in filters[size_key]:
            reason = f"{size_key} 필터 누락 또는 스키마 오류"
            print(f"판정: FAIL | 사유: {reason}")
            fail_list.append((pat_key, reason))
            continue

        pattern_mat = pat_info.get("input")
        cross_filter = filters[size_key]["Cross"]
        x_filter = filters[size_key]["X"]

        # 패턴과 필터의 N x N 크기 일치 여부 검증
        if (not is_valid_square_matrix(pattern_mat, n_size) or
            not is_valid_square_matrix(cross_filter, n_size) or
            not is_valid_square_matrix(x_filter, n_size)):
            reason = f"크기 불일치 (기대 크기: {n_size}×{n_size})"
            print(f"판정: FAIL | 사유: {reason}")
            fail_list.append((pat_key, reason))
            continue

        # 성능 측정용 샘플 저장 (크기별 최초 1개)
        if n_size not in bench_samples:
            bench_samples[n_size] = (pattern_mat, cross_filter)

        # MAC 연산 및 판정
        cross_score = mac_operation(pattern_mat, cross_filter)
        x_score = mac_operation(pattern_mat, x_filter)
        decision = judge_scores(cross_score, x_score, label_a="Cross", label_b="X")
        expected_label = normalize_label(pat_info.get("expected", ""))

        print(f"Cross 점수: {cross_score:.16f}" if decision == "UNDECIDED" else f"Cross 점수: {cross_score:.4f}")
        print(f"X 점수: {x_score:.16f}" if decision == "UNDECIDED" else f"X 점수: {x_score:.4f}")

        if decision == expected_label:
            pass_count += 1
            print(f"판정: {decision} | expected: {expected_label} | PASS")
        else:
            if decision == "UNDECIDED":
                reason = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
            else:
                reason = f"판정 불일치 (예측: {decision}, 정답: {expected_label})"
            print(f"판정: {decision} | expected: {expected_label} | FAIL ({reason})")
            fail_list.append((pat_key, reason))

    # [3] 성능 분석 (3x3 포함, 5x5, 13x13, 25x25)
    print("\n#---------------------------------------")
    print("# [3] 성능 분석 (평균/10회)")
    print("#---------------------------------------")
    print(f"{'크기':<10} {'평균 시간(ms)':<15} {'연산 횟수'}")
    print("-" * 38)

    sample_3x3 = [[0.0, 1.0, 0.0], [1.0, 1.0, 1.0], [0.0, 1.0, 0.0]]
    bench_samples[3] = (sample_3x3, sample_3x3)

    for size in sorted(bench_samples.keys()):
        pat_m, fil_m = bench_samples[size]
        avg_ms = measure_mac_time(pat_m, fil_m, repeat=10)
        print(f"{f'{size}×{size}':<10} {avg_ms:<15.4f} {size * size}")

    # [4] 결과 요약
    print("\n#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total_count}개")
    print(f"통과: {pass_count}개")
    print(f"실패: {len(fail_list)}개")

    if fail_list:
        print("\n실패 케이스:")
        for case_id, msg in fail_list:
            print(f"- {case_id}: {msg}")

# 9. 메인 실행 메뉴
def main():
    while True:
        print("\n=== Mini NPU Simulator ===")
        print("[모드 선택]")
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        print("0. 종료")
        
        choice = input("선택: ").strip()
        
        if choice == "1":
            run_mode_1()
        elif choice == "2":
            run_mode_2("data.json")
        elif choice == "0":
            print("시뮬레이터를 종료합니다.")
            break
        else:
            print("잘못된 입력입니다. 1, 2, 0 중에서 선택해 주세요.")

if __name__ == "__main__":
    main()
import math
import time

class MiniNPUSimulator:
    """  
    시뮬레이터의 핵심 기능을 관리하는 클래스
    """
    def __init__(self):
        """  
        epsilon 등 기본 설정값 초기화
        """
        # 허용오차 범위 : 0.1 X 10^9 = 0.000000001
        self.epsilon = 1e-9
        # 최소 반복 기준 : 10번
        self.min_iter = 10


    def normalize_label():
        """  
        입력 라벨을 표준 형식으로 변환
        """
        pass

    def validate_matrix(self, matrix, size):
        """  
        행렬 크기와 데이터 유효성 검사
        """
        reasons = []

        # 1. 리스트 여부 확인
        if not isinstance(matrix, list):
            reasons.append("행렬은 리스트 형식이어야 합니다.")
            return {
                "valid": False,
                "reasons": reasons
            }

        # 2. 행 개수 확인
        if len(matrix) != size:
            reasons.append(
                f"행 개수가 올바르지 않습니다. (기대값: {size}, 실제값: {len(matrix)})"
            )

        # 3. 각 행의 열 개수 및 원소 확인
        for row_index, row in enumerate(matrix):
            if not isinstance(row, list):
                reasons.append(f"{row_index + 1}번째 행이 리스트가 아닙니다.")
                continue

            if len(row) != size:
                reasons.append(
                    f"{row_index + 1}번째 행의 열 개수가 올바르지 않습니다."
                )

            for col_index, value in enumerate(row):
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    reasons.append(
                        f"{row_index + 1}행 {col_index + 1}열의 값이 숫자가 아닙니다."
                    )
                elif not math.isfinite(value):
                    reasons.append(
                        f"{row_index + 1}행 {col_index + 1}열의 값이 유효하지 않습니다."
                    )

        return {
            "valid": len(reasons) == 0,
            "reasons": reasons if reasons else None
        }

    def calculate_mac(self, pattern, filter):
        """  
        필터와 패턴의 MAC 점수 계산
        """

        # MAC 점수 초기화
        score = 0

        # MAC 연산
        for i in range(len(filter)):
            for j in range(len(filter[i])):
                score += filter[i][j] * pattern[i][j]

        # MAC 점수 반환
        return score


    def compare_scores(self, filter_a_mac, filter_b_mac):
        """  
        두 MAC 점수 비교 및 epsilon 적용\n
        "A", "B" 두개 패턴의 MAC 점수 중 가장 높은 쪽을 반환, 두 점수의 MAC 점수가 허용오차 범위 안일 경우 "UNDECIDED" 반환
        """
        # 두 패턴간의 점수 차이
        difference = abs(filter_a_mac - filter_b_mac)

        # 두 점수간의 차이가 허용오차 범위 안인 경우 "UNDECIDED" 반환
        if difference < self.epsilon:
            return "UNDECIDED"
        elif filter_a_mac > filter_b_mac:
            return "A"
        else:
            return "B"


    def classify_pattern(self, filter_a, filter_b, pattern):
        """  
        최종적으로 A, B, UNDECIDED 판정
        """

        filter_a_benchmark_mac = self.benchmark_mac(pattern, filter_a)
        filter_a_mac = filter_a_benchmark_mac['mac']
        filter_a_average_time = filter_a_benchmark_mac['average_time']

        filter_b_benchmark_mac = self.benchmark_mac(pattern, filter_b)
        filter_b_mac = filter_b_benchmark_mac['mac']
        filter_b_average_time = filter_b_benchmark_mac['average_time']

        average_time = (filter_a_average_time + filter_b_average_time) / 2

        result = self.compare_scores(filter_a_mac, filter_b_mac)

        return {
            "score_a": filter_a_mac,
            "score_b": filter_b_mac,
            "average_time": average_time,
            "result": result

        }


    def run_manual_mode(self):
        """  
        사용자 입력을 통한 3×3 패턴 분석\n
        """

        # 필터 A
        filter_a = self.input_matrix()

        print("==== 필터 A ====")
        for row in filter_a:
            print(row)

        # 필터 B
        filter_b = self.input_matrix()

        print("==== 필터 B ====")
        for row in filter_b:
            print(row)

        # 패턴
        pattern = self.input_matrix()

        print("==== 패턴 ====")
        for row in pattern:
            print(row)

        # MAC 점수 판단
        classify_pattern = self.classify_pattern(filter_a, filter_b, pattern)

        print("==== MAC 결과 ====")
        print(f"A 점수 : {classify_pattern['score_a']}")
        print(f"B 점수 : {classify_pattern['score_b']}")
        print(f"연산 시간(평균/{self.min_iter}) : {classify_pattern['average_time']} ms")
        print(f"판정 : {classify_pattern['result']}")


    def input_matrix(self):
        """  
        사용자에게 3×3 패턴을 입력받고 유효한지 확인하는 메서드\n
        3×3 필터 2개(A, B)를 “한 줄씩(공백 구분)” 입력받아 저장해야 한다.\n
        3×3 패턴을 동일한 방식으로 입력받아 저장해야 한다.\n
        입력 검증(최소 기준):\n
            행 수/열 수 불일치, 숫자 파싱 실패 시 안내 문구를 출력하고 재입력을 유도해야 한다.\n
            예: “입력 형식 오류: 각 줄에 3개의 숫자를 공백으로 구분해 입력하세요.”\n
        """

        # 반환할 행/열 초기화
        matrix = []

        while True:
            # 1. 사용자 입력
            user_input_txt = input("필터 A 입력 (숫자 9개): ")
    
            # 2. 앞뒤 공백 제거 및 공백 기준 분리
            user_input_list = user_input_txt.strip().split()
    
            # 3. 입력 개수 확인
            if len(user_input_list) != 9:
                print("오류: 숫자를 정확히 9개 입력해야 합니다.")
                continue
    
            # 4. 문자열을 숫자로 변환
            try:
                numbers = [float(user_input) for user_input in user_input_list]
            except ValueError:
                print("오류: 숫자만 입력할 수 있습니다.")
                continue
    
            # 5. 3x3 배열 생성
            matrix = [
                numbers[0:3],
                numbers[3:6],
                numbers[6:9]
            ]
    
            # 6. 행렬 유효성 검사
            validation = self.validate_matrix(matrix, 3)
    
            if not validation["valid"]:
                print("행렬 입력 오류:")
                for reason in validation["reasons"]:
                    print(f"- {reason}")
                continue
    
            break

        return matrix


    def load_json_data():
        """  
        data.json 파일 읽기
        """
        pass

    def run_json_test_mode():
        """  
        JSON 데이터의 전체 테스트 수행
        """
        pass

    def benchmark_mac(self, pattern, filter):
        """  
        정해진 최소 반복 기준에 따라 MAC 연산을 반복\n
        MAC 점수, 진행 시간, 평균 시간 3개를 반환\n
        """

         # 1. 연산 시작 시간
        start_time = time.perf_counter()

        # MAC 점수
        mac = 0

        # 2. MAC 연산 반복
        for _ in range(self.min_iter):
            mac = self.calculate_mac(pattern, filter)

        # 3. 연산 종료 시간
        end_time = time.perf_counter()
            
        # 4. 진행 시간 계산 (ms)
        taken_time = (end_time - start_time) * 1000

        # 5. 평균 진행 시간 계산 (ms)
        average_time = taken_time / self.min_iter

        return {
            "mac" : mac,
            "taken_time" : taken_time,
            "average_time" : average_time
        }


    def summarize_results():
        """  
        전체 테스트 결과 및 PASS/FAIL 집계
        """
        pass
import json
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


    def normalize_label(self, label):
        """  
        입력 라벨을 표준 형식으로 변환
        """
        if not isinstance(label, str):
            return None

        label = label.strip().lower()

        label_mapping = {
            "+": "Cross",
            "cross": "Cross",
            "a": "Cross",
            "x": "X",
            "b": "X",
            "undecided":"UNDECIDED"
        }

        return label_mapping.get(label)

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


    def load_json_data(self):
        """ 
        JSON 파일에서 퀴즈 데이터를 불러오는 메서드
        파일이 손상되었거나 읽기/쓰기 오류가 발생한 경우를 try/except 로 처리한다.
        """
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
                return data
        except json.JSONDecodeError:
            print("데이터 파일이 손상되었습니다.")

        except OSError as error:
            print(f"데이터 파일을 읽을 수 없습니다: {error}")

    def run_json_test_mode(self):
        """  
        JSON 데이터의 전체 테스트 수행
        """

        # JSON 데이터 로드
        print("==== JSON 데이터를 로드 합니다. ====")
        json_data = self.load_json_data()

        # 필터 데이터
        filters_data = json_data['filters']
        # 패턴 데이터
        patterns_data = json_data['patterns']

        mac_result_list = []

        # 패턴을 기준으로 반복문 실행
        for pattern_key in patterns_data:

            pattern_key_list = pattern_key.split("_")

            # 패턴의 키값을 _ 기준으로 나눈 뒤 0과 1번 인덱스를 합쳐 필터의 키값 생성
            filters_key = pattern_key_list[0] + "_" + pattern_key_list[1]
            # 필터 리스트를 가져온다
            filters = filters_data[filters_key]
            # + 필터
            filter_cross = filters['cross']
            # x 필터
            filter_x = filters['x']

            # MAC 연산을 돌릴 패턴
            pattern = patterns_data[pattern_key]['input']
            # 기대값
            expected = patterns_data[pattern_key]['expected']
            # 정규화 된 기대값
            normalize_expected = self.normalize_label(expected)

            # MAC 연산에 대한 
            mac_result = {
                "test_name": pattern_key,
                "size": pattern_key_list[1],
                "filter_cross_score": 0,
                "filter_x_score": 0,
                "expected": normalize_expected,
                "average_time": 0,
                "actual":"",
                "result": "",
                "reason": ""
            }

            # 행렬 유효성 검사
            json_test_validate_matrix = self.json_test_validate_matrix(filter_cross, filter_x, pattern, pattern_key_list[1])

            # 행열이 유효하지 않은 경우 continue
            if(json_test_validate_matrix['valid']):
                mac_result['result'] = "FAIL"
                mac_result['reason'] = json_test_validate_matrix['reasons']
                mac_result_list.append(mac_result)
                continue

            # MAC 연산 및 판정
            classify_pattern = self.classify_pattern(filter_cross, filter_x, pattern)

            normalize_actual = self.normalize_label(classify_pattern['result'])

            mac_result['filter_cross_score'] = classify_pattern['score_a']
            mac_result['filter_x_score'] = classify_pattern['score_b']
            mac_result['average_time'] = classify_pattern['average_time']
            mac_result['actual'] = normalize_actual

            # MAC 연산결과 판정
            if(normalize_actual == normalize_expected):
                mac_result['result'] = "PASS"
            else:
                mac_result['result'] = "FAIL"
                mac_result['reason'] = "패턴불일치"
                if(normalize_actual == "UNDECIDED"):
                    mac_result['reason'] = "동점(UNDECIDED) 처리 규칙에 따라 FAIL"

            mac_result_list.append(mac_result)

        self.summarize_results(mac_result_list)



            
    def json_test_validate_matrix(self, filter_cross, filter_x, pattern, size):
        """  
        run_json_test_mode 메서드 내부에 필터와 패턴의 행열이 유효한지 검사
        """
        
        validation = self.validate_matrix(filter_cross, size)

        if(validation['valid']):
            return {
                "valid": True,
                "reasons": "+ 필터 행열이 유효하지 않음."
            }
        
        validation = self.validate_matrix(filter_x, size)

        if(validation['valid']):
            return {
                "valid": True,
                "reasons": "X 필터 행열이 유효하지 않음."
            }
        
        validation = self.validate_matrix(pattern, size)

        if(validation['valid']):
            return {
                "valid": True,
                "reasons": "패턴 행열이 유효하지 않음."
            }

        return {
            "valid": False,
            "reasons": ""
        }
        

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


    def summarize_results(self, mac_result_list):
        """  
        전체 테스트 결과 및 PASS/FAIL 집계
        """
        total_count = len(mac_result_list)
        pass_count = 0
        fail_count = 0
        # 실패한 결과를 모아둔 리스트
        fail_case_list = []
        # 밴치마크한 결과를 요약하기 위한 딕셔너리
        benchmark_list = {}


        print("==== 패턴 분석 ====")
        for mac_result in mac_result_list:

            # 사이즈를 키값으로 각 사이즈별 키값이 있으면 경과 시간을 합산, 없으면 해당 키값을 생성
            if mac_result['size'] in benchmark_list:
                benchmark_list[mac_result['size']]['total_average_time'] += mac_result['average_time']
                benchmark_list[mac_result['size']]['count'] += 1
            else:
                benchmark_list[mac_result['size']] = {
                    "total_average_time":mac_result['average_time'],
                    "count":1,
                }

            if mac_result["result"] == "PASS":
                pass_count += 1
            else:
                fail_count += 1
                fail_case_list.append(f"{mac_result['test_name']} : {mac_result['reason']}")

            print(f"-- {mac_result['test_name']} --")
            print(f"Cross 점수: {mac_result['filter_cross_score']}")
            print(f"X 점수: {mac_result['filter_x_score']}")
            print(f"판정: {mac_result['actual']} | expected: {mac_result['expected']} | {mac_result['result']}")


        print(f"==== 성능분석(평균/{self.min_iter}회) ====")
        print("크기\t평균 시간(ms)\t\t연산횟수")
        for size, benchmark in benchmark_list.items():
            # 평균 시간 = 각 케이스별 평균시간의 합산 / 전체 합산수
            average_time = benchmark['total_average_time'] / benchmark['count']
            # 연산 횟수 = 행열의 제곱
            cal_count = int(size) ** 2
            print(f"{size}x{size}\t{average_time}\t{cal_count}")


        print("==== 결과 요약 ====")
        print(f"총 테스트: {total_count}개")
        print(f"통과: {pass_count}개")
        print(f"실패: {fail_count}개")
        print("")
        print("실패 케이스")
        
        for fail_case in fail_case_list:
            # 평균 시간 = 각 케이스별 평균시간의 합산 / 전체 합산수
            print(fail_case)

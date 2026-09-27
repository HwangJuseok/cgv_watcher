import Foundation

// 공통 데이터 (유지보수를 위해 한 곳에서 관리)
struct AppData {
    static let movies = ["30001323": "🪐 오디세이", "30001192": "🕷️ 스파이더맨"]
    static let theaters = ["0013": "용산아이파크몰", "0059": "영등포"]
    static let screens = ["IMAX": "IMAX", "SCREENX": "ScreenX", "2D": "일반 2D"]
}

// 서버로 보낼 감시 조건 요청 데이터
struct TargetRequest: Codable {
    let user_id: String
    let movie_code: String
    let theater_code: String
    let target_date: String
    let screen_type: String
}

// 서버에서 돌아오는 기본 응답 데이터
struct APIResponse: Codable {
    let status: String
    let message: String?
}

// 리스트 조회를 위한 응답 모델
struct UserTarget: Codable, Hashable {
    let movie_code: String
    let theater_code: String
    let target_date: String
    let screen_type: String
}

struct TargetListResponse: Codable {
    let status: String
    let data: [UserTarget]
}
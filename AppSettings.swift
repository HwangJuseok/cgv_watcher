import Foundation

/// 서버 주소, 텔레그램 ID처럼 코드에 하드코딩하면 안 되는 값들을
/// 기기의 UserDefaults에 저장/조회하는 헬퍼입니다.
/// 앱을 처음 실행하면 "설정" 탭에서 값을 입력해야 나머지 기능이 정상 동작합니다.
struct AppSettings {
    private static let baseURLKey = "cgvwatcher.baseURL"
    private static let userIdKey = "cgvwatcher.userId"

    static var baseURL: String {
        get { UserDefaults.standard.string(forKey: baseURLKey) ?? "" }
        set { UserDefaults.standard.set(newValue, forKey: baseURLKey) }
    }

    static var userId: String {
        get { UserDefaults.standard.string(forKey: userIdKey) ?? "" }
        set { UserDefaults.standard.set(newValue, forKey: userIdKey) }
    }

    /// 서버 주소와 사용자 ID가 모두 입력되었는지 여부
    static var isConfigured: Bool {
        !baseURL.trimmingCharacters(in: .whitespaces).isEmpty
            && !userId.trimmingCharacters(in: .whitespaces).isEmpty
    }
}

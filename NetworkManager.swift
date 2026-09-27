import Foundation

class NetworkManager: ObservableObject {
    // ⚠️ 서버 주소는 더 이상 코드에 하드코딩하지 않고, "설정" 탭에서 입력한 값을 사용합니다.
    private var baseURL: String { AppSettings.baseURL }

    func addTarget(target: TargetRequest) async -> String {
        guard !baseURL.isEmpty else { return "먼저 '설정' 탭에서 서버 주소를 입력해 주세요." }
        guard let url = URL(string: "\(baseURL)/targets") else { return "잘못된 URL입니다." }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(target)
            let (data, response) = try await URLSession.shared.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                return "서버 오류가 발생했습니다."
            }
            
            let result = try JSONDecoder().decode(APIResponse.self, from: data)
            return result.message ?? "조건 등록이 완료되었습니다!"
        } catch {
            return "서버 통신 실패: \(error.localizedDescription)"
        }
    }
    
    func fetchTargets(userId: String) async -> [UserTarget] {
        guard !baseURL.isEmpty else { return [] }
        guard let url = URL(string: "\(baseURL)/targets/\(userId)") else { return [] }
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let result = try JSONDecoder().decode(TargetListResponse.self, from: data)
            return result.data
        } catch {
            print("목록 불러오기 실패: \(error)")
            return []
        }
    }
    
    func deleteTarget(target: TargetRequest) async -> Bool {
        guard !baseURL.isEmpty else { return false }
        guard let url = URL(string: "\(baseURL)/targets") else { return false }
        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        do {
            request.httpBody = try JSONEncoder().encode(target)
            let (_, response) = try await URLSession.shared.data(for: request)
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else { return false }
            return true
        } catch {
            return false
        }
    }
}

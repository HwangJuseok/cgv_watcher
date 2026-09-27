import SwiftUI

struct TargetListView: View {
    @StateObject private var networkManager = NetworkManager()
    @State private var targets: [UserTarget] = []
    
    // 본인의 텔레그램 ID를 입력해 줘
    let userId = "123456789" 
    
    var body: some View {
        NavigationView {
            List {
                ForEach(targets, id: \.self) { target in
                    VStack(alignment: .leading, spacing: 5) {
                        Text(AppData.movies[target.movie_code] ?? "알 수 없는 영화")
                            .font(.headline)
                        
                        HStack {
                            Text(AppData.theaters[target.theater_code] ?? "")
                            Text("|")
                            Text(formatDateString(target.target_date))
                            Text("|")
                            Text(AppData.screens[target.screen_type] ?? "")
                                .foregroundColor(.blue)
                        }
                        .font(.subheadline)
                        .foregroundColor(.gray)
                    }
                    .padding(.vertical, 4)
                }
                .onDelete(perform: deleteItems)
            }
            .navigationTitle("감시 목록")
            .onAppear {
                loadData()
            }
            .refreshable {
                loadData() // 당겨서 새로고침 지원
            }
        }
    }
    
    func loadData() {
        Task {
            targets = await networkManager.fetchTargets(userId: userId)
        }
    }
    
    func deleteItems(at offsets: IndexSet) {
        for index in offsets {
            let item = targets[index]
            let requestItem = TargetRequest(
                user_id: userId, 
                movie_code: item.movie_code, 
                theater_code: item.theater_code, 
                target_date: item.target_date, 
                screen_type: item.screen_type
            )
            
            Task {
                let success = await networkManager.deleteTarget(target: requestItem)
                if success {
                    targets.remove(at: index)
                }
            }
        }
    }
    
    // "20260901"을 "26년 9월 1일"로 보기 좋게 변환
    func formatDateString(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyyMMdd"
        if let date = formatter.date(from: dateString) {
            formatter.dateFormat = "yy년 M월 d일"
            return formatter.string(from: date)
        }
        return dateString
    }
}
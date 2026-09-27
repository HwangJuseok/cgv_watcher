import SwiftUI

struct ContentView: View {
    @StateObject private var networkManager = NetworkManager()
    
    @State private var selectedMovie = "30001323"
    @State private var selectedTheater = "0013"
    @State private var selectedScreen = "IMAX"
    
    // 달력 기본값을 오늘로 설정
    @State private var selectedDate = Date()
    
    @State private var alertMessage = ""
    @State private var showAlert = false
    
    var body: some View {
        NavigationView {
            Form {
                if !AppSettings.isConfigured {
                    Section {
                        Label("먼저 '설정' 탭에서 서버 주소와 텔레그램 ID를 입력해 주세요.", systemImage: "exclamationmark.triangle")
                            .foregroundColor(.orange)
                    }
                }

                Section(header: Text("예매 감시 조건 설정")) {
                    Picker("영화", selection: $selectedMovie) {
                        ForEach(AppData.movies.keys.sorted(), id: \.self) { key in
                            Text(AppData.movies[key] ?? "").tag(key)
                        }
                    }
                    Picker("영화관", selection: $selectedTheater) {
                        ForEach(AppData.theaters.keys.sorted(), id: \.self) { key in
                            Text(AppData.theaters[key] ?? "").tag(key)
                        }
                    }
                    Picker("상영관 타입", selection: $selectedScreen) {
                        ForEach(AppData.screens.keys.sorted(), id: \.self) { key in
                            Text(AppData.screens[key] ?? "").tag(key)
                        }
                    }
                    
                    // 한국어 달력 위젯
                    DatePicker("관람 날짜", selection: $selectedDate, displayedComponents: .date)
                        .environment(\.locale, Locale(identifier: "ko_KR"))
                }
                
                Button(action: submitTarget) {
                    Text("감시 조건 등록하기")
                        .font(.headline)
                        .frame(maxWidth: .infinity)
                        .foregroundColor(.white)
                        .padding()
                        .background(AppSettings.isConfigured ? Color.blue : Color.gray)
                        .cornerRadius(10)
                }
                .disabled(!AppSettings.isConfigured)
            }
            .navigationTitle("CGV 알리미 리모컨")
            .alert(isPresented: $showAlert) {
                Alert(title: Text("알림"), message: Text(alertMessage), dismissButton: .default(Text("확인")))
            }
        }
    }
    
    // Date() 객체를 서버가 원하는 "YYYYMMDD" 형식의 문자열로 변환
    private var formattedTargetDate: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyyMMdd"
        return formatter.string(from: selectedDate)
    }
    
    func submitTarget() {
        let target = TargetRequest(
            user_id: AppSettings.userId,
            movie_code: selectedMovie,
            theater_code: selectedTheater,
            target_date: formattedTargetDate,
            screen_type: selectedScreen
        )
        
        Task {
            alertMessage = await networkManager.addTarget(target: target)
            showAlert = true
        }
    }
}

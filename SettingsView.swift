import SwiftUI

struct SettingsView: View {
    @State private var serverURL: String = AppSettings.baseURL
    @State private var telegramId: String = AppSettings.userId
    @State private var showSavedAlert = false

    var body: some View {
        NavigationView {
            Form {
                Section(
                    header: Text("서버 주소"),
                    footer: Text("백엔드가 실행 중인 서버 주소를 입력하세요. 예: http://123.45.67.89:8000")
                ) {
                    TextField("http://서버주소:8000", text: $serverURL)
                        .keyboardType(.URL)
                        .textInputAutocapitalization(.never)
                        .disableAutocorrection(true)
                }

                Section(
                    header: Text("내 텔레그램 ID"),
                    footer: Text("텔레그램에서 @userinfobot 등에게 말을 걸면 본인의 숫자 ID를 확인할 수 있습니다.")
                ) {
                    TextField("예: 123456789", text: $telegramId)
                        .keyboardType(.numberPad)
                }

                Section {
                    Button("저장하기") {
                        AppSettings.baseURL = serverURL.trimmingCharacters(in: .whitespaces)
                        AppSettings.userId = telegramId.trimmingCharacters(in: .whitespaces)
                        showSavedAlert = true
                    }
                    .frame(maxWidth: .infinity, alignment: .center)
                }
            }
            .navigationTitle("설정")
            .alert("저장되었습니다", isPresented: $showSavedAlert) {
                Button("확인", role: .cancel) {}
            }
        }
    }
}

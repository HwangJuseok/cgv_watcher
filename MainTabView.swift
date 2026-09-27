import SwiftUI

struct MainTabView: View {
    var body: some View {
        TabView {
            ContentView()
                .tabItem {
                    Label("조건 등록", systemImage: "plus.circle")
                }
            
            TargetListView()
                .tabItem {
                    Label("감시 목록", systemImage: "list.bullet")
                }

            SettingsView()
                .tabItem {
                    Label("설정", systemImage: "gearshape")
                }
        }
    }
}

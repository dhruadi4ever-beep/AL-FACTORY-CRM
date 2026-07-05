package com.aryanlace

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

private data class FeatureCard(val title: String, val body: String)

@Composable
fun ReportsAdminProductivityScreen() {
    val features = remember {
        listOf(
            FeatureCard("Report Center", "Generate production, inventory, employee, job-work, bobbin, and finance reports with filters and export options."),
            FeatureCard("Admin Console", "Manage system settings, audit trail, backup/restore, and secure single-admin sessions."),
            FeatureCard("Productivity Hub", "Global search, command center, quick actions, recent favorites, and smart navigation."),
        )
    }

    var search by remember { mutableStateOf("production") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(text = "Reports, Admin & Productivity", style = MaterialTheme.typography.headlineMedium)
        Text(text = "Centralized reporting, admin controls, and productivity workflows")

        OutlinedTextField(value = search, onValueChange = { search = it }, label = { Text("Global Search") }, modifier = Modifier.fillMaxWidth())

        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
            items(features) { feature ->
                Card(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(12.dp)) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text(text = feature.title, style = MaterialTheme.typography.titleMedium)
                        Text(text = feature.body)
                    }
                }
            }
        }
    }
}
